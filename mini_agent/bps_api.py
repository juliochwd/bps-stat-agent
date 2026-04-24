#!/usr/bin/env python3
"""BPS WebAPI Python Client Library.

A comprehensive client for Badan Pusat Statistik (Statistics Indonesia) Web API.
Supports all 44+ endpoints including Domain, Subjects, Variables, Dynamic Data,
Static Tables, Press Releases, Publications, SDGs, Census, SIMDASI, and more.

Usage:
    from bps_api import BPSAPI

    api = BPSAPI("your_api_key_here")

    # Get all domains
    domains = api.get_domains()

    # Get subjects for central (0000)
    subjects = api.get_subjects()

    # Get dynamic data
    data = api.get_data(var=184, th=117)

    # Get press releases
    press = api.get_press_releases(year=2024)

    # Get census data
    census_events = api.get_census_events()

    # Get SIMDASI data
    provinces = api.get_simdasi_provinces()
"""

from typing import Any

import requests


class BPSAPIError(Exception):
    """Exception raised for BPS API errors."""

    def __init__(self, message: str, response: str | None = None):
        """Initialize BPSAPIError.

        Args:
            message: Error message
            response: Optional raw response text
        """
        super().__init__(message)
        self.response = response


class BPSMaterial:
    """Wrapper for BPS publication and press release content.

    Provides lazy loading of PDF content and metadata access.
    Inspired by STADATA Material class.
    """

    def __init__(self, data: dict, app_id: str | None = None):
        """Initialize BPSMaterial.

        Args:
            data: Publication/press release data from BPS API
            app_id: Optional API key for authenticated requests
        """
        self.data = data
        self._app_id = app_id
        self._content: bytes | None = None

    @property
    def content(self) -> bytes:
        """Lazy load and return PDF content."""
        if self._content is None:
            pdf_url = self.data.get("pdf")
            if not pdf_url:
                raise BPSAPIError("No PDF URL in material data")
            resp = requests.get(pdf_url, timeout=60)
            resp.raise_for_status()
            self._content = resp.content
        return self._content

    def download(self, filepath: str) -> None:
        """Download PDF content to file.

        Args:
            filepath: Full path where PDF will be saved
        """
        with open(filepath, "wb") as f:
            f.write(self.content)

    def desc(self) -> dict:
        """Return material metadata."""
        return self.data


class BPSAPI:
    """Client for BPS (Badan Pusat Statistik) Web API."""

    BASE_URL = "https://webapi.bps.go.id"
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }

    def __init__(self, app_id: str):
        """Initialize BPS API client.

        Args:
            app_id: Your BPS API application ID (key token)
        """
        self.app_id = app_id
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)

    def _request(self, url: str, params: dict | None = None) -> dict[str, Any]:
        """Make a request to BPS API.

        Args:
            url: Full API URL
            params: Query parameters

        Returns:
            JSON response as dict

        Raises:
            BPSAPIError: If API returns HTTP error, non-OK status, or invalid JSON
        """
        # Copy params to avoid mutating caller's dict
        request_params = {**(params or {}), "key": self.app_id}
        resp = self.session.get(url, params=request_params, timeout=60)
        resp.raise_for_status()
        try:
            result = resp.json()
            # Validate API status field if present (STADATA pattern)
            # Only check status when field exists and is not OK
            if "status" in result and result["status"] != "OK":
                message = result.get("message", "Unknown API error")
                raise BPSAPIError(message, response=resp.text)
            return result
        except ValueError as e:
            raise BPSAPIError(f"Invalid JSON response from {url}: {e}", response=resp.text)

    def _list(self, model: str, domain: str = "0000", **kwargs) -> dict[str, Any]:
        """Generic list endpoint caller.

        Args:
            model: Model type (subject, var, data, etc.)
            domain: Domain code (4-digit string)
            **kwargs: Additional parameters

        Returns:
            API response dict
        """
        params = {"model": model, "domain": domain, **kwargs}
        return self._request(f"{self.BASE_URL}/v1/api/list", params)

    def _view(
        self, model: str, id: Any, domain: str = "0000", lang: str = "ind", **kwargs
    ) -> dict[str, Any]:
        """Generic view/detail endpoint caller.

        Args:
            model: Model type
            id: Resource ID
            domain: Domain code
            lang: Language (ind/eng)
            **kwargs: Additional parameters

        Returns:
            API response dict
        """
        params = {"model": model, "domain": domain, "lang": lang, "id": id, **kwargs}
        return self._request(f"{self.BASE_URL}/v1/api/view", params)

    def _format_domain(self, domain: str) -> str:
        """Ensure domain is 4-digit zero-padded string.

        BPS uses 4-digit domain codes: 0000 (national), 5300 (NTT province),
        5371 (Nagekeo district), etc.

        Args:
            domain: Domain ID (int or str)

        Returns:
            Zero-padded 4-digit domain string
        """
        return f"{int(domain):04d}"

    def _extract_data(self, response: dict) -> list:
        """Extract data list from paginated response.

        Args:
            response: API response dict

        Returns:
            List of data items (data[1])
        """
        # Handle direct data array format (SIMDASI-style)
        # If response has "data" as a list, check its structure
        if "data" in response and isinstance(response.get("data"), list):
            data = response.get("data", [])
            # Check if it's the paginated format: data[0]=pagination(dict), data[1]=items(list)
            if isinstance(data, list) and len(data) > 1 and isinstance(data[0], dict) and isinstance(data[1], list):
                return data[1] if data[1] is not None else []
            # Check for SIMDASI nested format: data[1] contains another dict with "data" key
            if isinstance(data, list) and len(data) > 1 and isinstance(data[1], dict) and "data" in data[1]:
                nested_data = data[1].get("data")
                if isinstance(nested_data, list):
                    return nested_data
            # Direct list format - data is already a list of items (no pagination dict)
            if data and isinstance(data[0], dict) and ("page" in data[0] or "pagination" in data[0]):
                # This is paginated format where data[1] is None (data[0] is pagination metadata)
                return []
            # Only return [] for data[1]=None if data-availability indicates valid response
            if response.get("data-availability") == "available" and len(data) > 1 and data[1] is None:
                return []
            return data
        # Handle standard BPS API response with data-availability
        if response.get("data-availability") != "available":
            return []
        data = response.get("data", [])
        if isinstance(data, list) and len(data) > 1:
            return data[1] if data[1] is not None else []
        return []

    def _extract_paginated(self, response: dict) -> dict:
        """Extract pagination info and data from response.

        Args:
            response: API response dict

        Returns:
            Dict with 'pagination' and 'items' keys
        """
        result = {"pagination": {}, "items": []}
        if response.get("data-availability") != "available":
            return result
        data = response.get("data", [])
        if isinstance(data, list) and len(data) >= 2:
            result["pagination"] = data[0] if data[0] else {}
            result["items"] = data[1] if data[1] else []
        return result

    # ================================================================
    # DOMAIN ENDPOINTS
    # ================================================================

    def get_domains(self, type: str = "all", prov: str | None = None) -> list[dict]:
        """Get all BPS statistic domains.

        Args:
            type: 'all', 'prov', 'kab', 'kabbyprov'
            prov: Province ID (required when type='kabbyprov')

        Returns:
            List of domain objects with domain_id, domain_name, domain_url
        """
        params = {"type": type}
        if prov:
            params["prov"] = prov
        resp = self._request(f"{self.BASE_URL}/v1/api/domain", params)
        return self._extract_data(resp)

    def get_provinces(self) -> list[dict]:
        """Get all province domains."""
        return self.get_domains(type="prov")

    def get_regencies(self, prov_id: str | None = None) -> list[dict]:
        """Get regency/city domains.

        Args:
            prov_id: Province ID to filter by (4-digit). If None, returns all.
        """
        if prov_id:
            return self.get_domains(type="kabbyprov", prov=prov_id)
        return self.get_domains(type="kab")

    # ================================================================
    # SUBJECT ENDPOINTS
    # ================================================================

    def get_subject_categories(
        self, domain: str = "0000", lang: str = "ind"
    ) -> list[dict]:
        """Get subject categories."""
        return self._extract_data(self._list("subcat", domain, lang=lang))

    def get_subjects(
        self,
        domain: str = "0000",
        subcat: int | None = None,
        lang: str = "ind",
        page: int = 1,
    ) -> dict:
        """Get subjects with pagination info.

        Args:
            domain: Domain code
            subcat: Subject category ID filter
            lang: Language
            page: Page number

        Returns:
            Dict with 'pagination' and 'items'
        """
        params = {"lang": lang, "page": page}
        if subcat:
            params["subcat"] = subcat
        return self._extract_paginated(self._list("subject", domain, **params))

    # ================================================================
    # VARIABLE ENDPOINTS
    # ================================================================

    def get_variables(
        self,
        domain: str = "0000",
        subject: int | None = None,
        year: int | None = None,
        lang: str = "ind",
        page: int = 1,
    ) -> dict:
        """Get variables with pagination."""
        params = {"lang": lang, "page": page}
        if subject:
            params["subject"] = subject
        if year:
            params["year"] = year
        return self._extract_paginated(self._list("var", domain, **params))

    def get_periods(
        self,
        domain: str = "0000",
        var: int | None = None,
        lang: str = "ind",
        page: int = 1,
    ) -> dict:
        """Get period data."""
        params = {"lang": lang, "page": page}
        if var:
            params["var"] = var
        return self._extract_paginated(self._list("th", domain, **params))

    def get_vertical_variables(
        self,
        domain: str = "0000",
        var: int | None = None,
        lang: str = "ind",
        page: int = 1,
    ) -> dict:
        """Get vertical variables."""
        params = {"lang": lang, "page": page}
        if var:
            params["var"] = var
        return self._extract_paginated(self._list("vervar", domain, **params))

    def get_derived_variables(
        self,
        domain: str = "0000",
        var: int | None = None,
        lang: str = "ind",
        page: int = 1,
    ) -> dict:
        """Get derived variables."""
        params = {"lang": lang, "page": page}
        if var:
            params["var"] = var
        return self._extract_paginated(self._list("turvar", domain, **params))

    def get_derived_periods(
        self,
        domain: str = "0000",
        var: int | None = None,
        lang: str = "ind",
        page: int = 1,
    ) -> dict:
        """Get derived period data."""
        params = {"lang": lang, "page": page}
        if var:
            params["var"] = var
        return self._extract_paginated(self._list("turth", domain, **params))

    def get_units(self, domain: str = "0000", lang: str = "ind", page: int = 1) -> dict:
        """Get unit data."""
        return self._extract_paginated(self._list("unit", domain, lang=lang, page=page))

    # ================================================================
    # DYNAMIC DATA
    # ================================================================

    def get_data(
        self,
        var: int,
        th: int,
        domain: str = "0000",
        turvar: int | None = None,
        vervar: int | None = None,
        turth: int | None = None,
        lang: str = "ind",
    ) -> dict[str, Any]:
        """Get dynamic data values.

        Args:
            var: Variable ID (required)
            th: Period data ID (required, supports ranges: "2;3", "2:6")
            domain: Domain code
            turvar: Derived variable ID
            vervar: Vertical variable ID
            turth: Derived period ID
            lang: Language

        Returns:
            Full response dict with var, turvar, vervar, tahun, turtahun, datacontent
        """
        params = {"var": var, "th": th, "lang": lang}
        if turvar is not None:
            params["turvar"] = turvar
        if vervar is not None:
            params["vervar"] = vervar
        if turth is not None:
            params["turth"] = turth
        return self._list("data", domain, **params)

    def get_decoded_data(
        self,
        var: int,
        th: int,
        domain: str = "0000",
        turvar: int | None = None,
        vervar: int | None = None,
        turth: int | None = None,
        lang: str = "ind",
    ) -> dict[str, Any]:
        """Get dynamic data with decoded values (human-readable format).

        This method calls get_data() and decodes the datacontent dict
        into a structured format with region labels and actual values.

        Args:
            var: Variable ID (required)
            th: Period data ID (required, supports ranges: "2;3", "2:6")
            domain: Domain code
            turvar: Derived variable ID
            vervar: Vertical variable ID
            turth: Derived period ID
            lang: Language

        Returns:
            Dict with:
            - status: API status
            - variable: Variable info (label, unit, subject)
            - year: Year/period label
            - regions: List of region labels
            - data: List of (region_id, region_label, value) tuples
            - raw_data: Original datacontent dict
        """
        result = self.get_data(var=var, th=th, domain=domain, turvar=turvar,
                               vervar=vervar, turth=turth, lang=lang)

        if result.get("status") != "OK":
            return result

        # Build region map from vervar
        region_map = {}
        for r in result.get("vervar", []):
            region_map[r["val"]] = r["label"]

        # Decode datacontent dict
        # Key format: "<region_id><var_id><year>0" or similar encoding
        # Value is already a float
        decoded_data = []
        datacontent = result.get("datacontent", {})

        if isinstance(datacontent, dict):
            for key, value in datacontent.items():
                key_str = str(key)
                # Extract region_id by finding it at start of key
                region_id = self._extract_region_id(key_str, var)
                if region_id:
                    decoded_data.append({
                        "region_id": region_id,
                        "region_label": region_map.get(region_id, f"Unknown({region_id})"),
                        "value": float(value)
                    })
        elif isinstance(datacontent, list):
            # List format: [region_id, value, ...] interleaved or as tuples
            for i in range(0, len(datacontent) - 1, 2):
                if i + 1 < len(datacontent):
                    decoded_data.append({
                        "region_id": datacontent[i],
                        "region_label": region_map.get(datacontent[i], f"Unknown({datacontent[i]})"),
                        "value": float(datacontent[i + 1])
                    })

        # Sort by region_id
        decoded_data.sort(key=lambda x: x["region_id"])

        # Get year label
        tahun_list = result.get("tahun", [])
        year_label = tahun_list[0].get("label") if tahun_list else str(th)

        # Get variable info
        var_list = result.get("var", [])
        variable_info = var_list[0] if var_list else {}

        return {
            "status": "OK",
            "variable": {
                "id": variable_info.get("val"),
                "label": variable_info.get("label"),
                "unit": variable_info.get("unit"),
                "subject": variable_info.get("subj"),
                "note": variable_info.get("note", ""),
            },
            "year": year_label,
            "regions": [r["label"] for r in result.get("vervar", [])],
            "data": decoded_data,
            "raw_data": datacontent,
        }

    def _extract_region_id(self, key_str: str, var_id: int) -> int | None:
        """Extract region ID from encoded key string.

        Key format: "<region_id><var_id><year>0" where region_id is 1-2 digits.
        """
        var_str = str(var_id)
        for length in [2, 1]:  # Try 2-digit first, then 1-digit
            if len(key_str) > length:
                potential_region = key_str[:length]
                remaining = key_str[length:]
                if remaining.startswith(var_str):
                    try:
                        return int(potential_region)
                    except ValueError:
                        pass
        return None

    # ===============================================================
    # STATIC TABLES
    # ===============================================================

    def get_static_tables(
        self,
        domain: str = "0000",
        year: int | None = None,
        keyword: str | None = None,
        lang: str = "ind",
        page: int = 1,
    ) -> dict:
        """Get static tables list."""
        params = {"lang": lang, "page": page}
        if year:
            params["year"] = year
        if keyword:
            params["keyword"] = keyword
        return self._extract_paginated(self._list("statictable", domain, **params))

    def get_static_table_detail(
        self, table_id: int, domain: str = "0000", lang: str = "ind"
    ) -> dict:
        """Get static table detail with HTML content."""
        return self._view("statictable", table_id, domain, lang)

    def get_dynamic_tables(
        self,
        domain: str = "0000",
        year: int | None = None,
        keyword: str | None = None,
        lang: str = "ind",
        page: int = 1,
    ) -> dict:
        """Get dynamic tables list.

        Dynamic tables are interactive statistical tables with
        variable/period breakdowns, different from static tables.
        """
        params = {"lang": lang, "page": page}
        if year:
            params["year"] = year
        if keyword:
            params["keyword"] = keyword
        return self._extract_paginated(self._list("dynamictable", domain, **params))

    def get_dynamic_table_detail(
        self, table_id: int, domain: str = "0000", lang: str = "ind"
    ) -> dict:
        """Get dynamic table detail."""
        return self._view("dynamictable", table_id, domain, lang)

    # ================================================================
    # PRESS RELEASES
    # ================================================================

    def get_press_releases(
        self,
        domain: str = "0000",
        year: int | None = None,
        month: int | None = None,
        keyword: str | None = None,
        lang: str = "ind",
        page: int = 1,
    ) -> dict:
        """Get press releases list."""
        params = {"lang": lang, "page": page}
        if year:
            params["year"] = year
        if month:
            params["month"] = month
        if keyword:
            params["keyword"] = keyword
        return self._extract_paginated(self._list("pressrelease", domain, **params))

    def get_press_release_detail(
        self, brs_id: int, domain: str = "0000", lang: str = "ind"
    ) -> BPSMaterial:
        """Get press release detail as BPSMaterial.

        Args:
            brs_id: Press release ID
            domain: Domain code
            lang: Language (ind/eng)

        Returns:
            BPSMaterial object with lazy-loading PDF content
        """
        data = self._view("pressrelease", brs_id, domain, lang)
        return BPSMaterial(data.get("data", {}), self.app_id)

    # ================================================================
    # PUBLICATIONS
    # ================================================================

    def get_publications(
        self,
        domain: str = "0000",
        year: int | None = None,
        month: int | None = None,
        keyword: str | None = None,
        lang: str = "ind",
        page: int = 1,
    ) -> dict:
        """Get publications list."""
        params = {"lang": lang, "page": page}
        if year:
            params["year"] = year
        if month:
            params["month"] = month
        if keyword:
            params["keyword"] = keyword
        return self._extract_paginated(self._list("publication", domain, **params))

    def get_publication_detail(
        self, pub_id: str, domain: str = "0000", lang: str = "ind"
    ) -> BPSMaterial:
        """Get publication detail as BPSMaterial.

        Args:
            pub_id: Publication ID
            domain: Domain code
            lang: Language (ind/eng)

        Returns:
            BPSMaterial object with lazy-loading PDF content
        """
        data = self._view("publication", pub_id, domain, lang)
        return BPSMaterial(data.get("data", {}), self.app_id)

    # ================================================================
    # INDICATORS & INFOGRAPHICS
    # ================================================================

    def get_indicators(
        self,
        domain: str = "0000",
        var: int | None = None,
        lang: str = "ind",
        page: int = 1,
    ) -> dict:
        """Get strategic indicators."""
        params = {"lang": lang, "page": page}
        if var:
            params["var"] = var
        return self._extract_paginated(self._list("indicators", domain, **params))

    def get_infographics(
        self,
        domain: str = "0000",
        keyword: str | None = None,
        lang: str = "ind",
        page: int = 1,
    ) -> dict:
        """Get infographics."""
        params = {"lang": lang, "page": page}
        if keyword:
            params["keyword"] = keyword
        return self._extract_paginated(self._list("infographic", domain, **params))

    def get_infographic_detail(
        self, infographic_id: str, domain: str = "0000", lang: str = "ind"
    ) -> dict:
        """Get infographic detail with image URL and description."""
        return self._view("infographic", infographic_id, domain, lang)

    # ================================================================
    # GLOSARIUM
    # ================================================================

    def get_glossary(
        self, prefix: str | None = None, perpage: int = 10, page: int = 1
    ) -> dict:
        """Get glossary terms."""
        params = {"perpage": perpage, "page": page}
        if prefix:
            params["prefix"] = prefix
        return self._extract_paginated(self._list("glosarium", "0000", **params))

    def get_glossary_detail(
        self, glossary_id: int, lang: str = "ind"
    ) -> dict:
        """Get glossary term detail."""
        return self._view("glosarium", glossary_id, "0000", lang)

    # ================================================================
    # SDGs & SDDS
    # ================================================================

    def get_sdgs(self, goal: str | None = None) -> dict:
        """Get SDGs indicators.

        Args:
            goal: Goal number "1" to "17"
        """
        params = {}
        if goal:
            params["goal"] = goal
        return self._extract_paginated(self._list("sdgs", "0000", **params))

    def get_sdds(self) -> dict:
        """Get SDDS indicators."""
        return self._extract_paginated(self._list("sdds", "0000"))

    # ================================================================
    # NEWS
    # ================================================================

    def get_news(
        self,
        domain: str = "0000",
        newscat: int | None = None,
        year: int | None = None,
        month: int | None = None,
        keyword: str | None = None,
        lang: str = "ind",
        page: int = 1,
    ) -> dict:
        """Get news list."""
        params = {"lang": lang, "page": page}
        if newscat:
            params["newscat"] = newscat
        if year:
            params["year"] = year
        if month:
            params["month"] = month
        if keyword:
            params["keyword"] = keyword
        return self._extract_paginated(self._list("news", domain, **params))

    def get_news_detail(
        self, news_id: int, domain: str = "0000", lang: str = "ind"
    ) -> dict:
        """Get news detail."""
        return self._view("news", news_id, domain, lang)

    def get_news_categories(
        self, domain: str = "0000", lang: str = "ind"
    ) -> list[dict]:
        """Get news categories."""
        return self._extract_data(self._list("newscategory", domain, lang=lang))

    # ================================================================
    # CSA (Custom Statistical Areas)
    # ================================================================

    def get_csa_categories(self, domain: str = "0000") -> list[dict]:
        """Get CSA subject categories."""
        return self._extract_data(self._list("subcatcsa", domain))

    def get_csa_subjects(
        self, domain: str = "0000", subcat: str | None = None
    ) -> dict:
        """Get CSA subjects."""
        params = {}
        if subcat:
            params["subcat"] = subcat
        return self._extract_paginated(self._list("subjectcsa", domain, **params))

    def get_csa_tables(
        self,
        domain: str = "0000",
        subject: int | None = None,
        page: int = 1,
        perpage: int = 10,
    ) -> dict:
        """Get CSA table statistics."""
        params = {"page": page, "perpage": perpage}
        if subject:
            params["subject"] = subject
        return self._extract_paginated(self._list("tablestatistic", domain, **params))

    def get_csa_table_detail(
        self, table_id: str, year: int | None = None, lang: str = "ind", domain: str = "0000"
    ) -> dict:
        """Get detail of a CSA table statistic."""
        params = {"model": "tablestatistic", "domain": domain, "lang": lang, "id": table_id}
        if year is not None:
            params["year"] = year
        return self._request(f"{self.BASE_URL}/v1/api/view", params)

    # ================================================================
    # FOREIGN TRADE
    # ================================================================

    def get_foreign_trade(
        self, sumber: int, kodehs: int, tahun: str, periode: int = 1, jenishs: int = 1
    ) -> dict[str, Any]:
        """Get foreign trade (export/import) data.

        Args:
            sumber: 1=Export, 2=Import
            kodehs: HS Code
            tahun: Year (e.g., "2024")
            periode: 1=monthly, 2=annually
            jenishs: 1=Two digit, 2=Full HS Code

        Returns:
            Response with metadata and data arrays
        """
        params = {
            "sumber": sumber,
            "kodehs": kodehs,
            "tahun": tahun,
            "periode": periode,
            "jenishs": jenishs,
        }
        return self._request(f"{self.BASE_URL}/v1/api/dataexim", params)

    # ================================================================
    # STATISTICAL CLASSIFICATIONS (KBLI)
    # ================================================================

    def get_kbli(
        self,
        year: int = 2020,
        level: str | None = None,
        page: int = 1,
        perpage: int = 10,
    ) -> dict:
        """Get KBLI (industrial classification).

        Args:
            year: 2009, 2015, 2017, or 2020
            level: 'kategori', 'golongan pokok', 'golongan', 'subgolongan', 'kelompok'
        """
        model = f"kbli{year}"
        params = {"page": page, "perpage": perpage}
        if level:
            params["level"] = level
        return self._extract_paginated(self._list(model, "0000", **params))

    def get_kbli_detail(
        self, kbli_id: str, year: int = 2020, lang: str = "ind"
    ) -> dict:
        """Get KBLI classification detail."""
        model = f"kbli{year}"
        return self._view(model, kbli_id, "0000", lang)

    # ================================================================
    # CENSUS DATA (sensus.bps.go.id)
    # ================================================================

    def get_census_events(self) -> list[dict]:
        """Get list of census events."""
        resp = self._request(
            f"{self.BASE_URL}/v1/api/interoperabilitas/datasource/sensus/id/37/"
        )
        return self._extract_data(resp)

    def get_census_topics(self, kegiatan: str) -> list[dict]:
        """Get census data topics.

        Args:
            kegiatan: Census event ID (e.g., 'sp2020')
        """
        resp = self._request(
            f"{self.BASE_URL}/v1/api/interoperabilitas/datasource/sensus/id/38/",
            {"kegiatan": kegiatan},
        )
        return self._extract_data(resp)

    def get_census_areas(self, kegiatan: str) -> list[dict]:
        """Get census event areas."""
        resp = self._request(
            f"{self.BASE_URL}/v1/api/interoperabilitas/datasource/sensus/id/39/",
            {"kegiatan": kegiatan},
        )
        return self._extract_data(resp)

    def get_census_datasets(self, kegiatan: str, topik: int) -> list[dict]:
        """Get available census datasets."""
        resp = self._request(
            f"{self.BASE_URL}/v1/api/interoperabilitas/datasource/sensus/id/40/",
            {"kegiatan": kegiatan, "topik": topik},
        )
        return self._extract_data(resp)

    def get_census_data(self, kegiatan: str, wilayah_sensus: int, dataset: int) -> dict:
        """Get actual census microdata."""
        return self._request(
            f"{self.BASE_URL}/v1/api/interoperabilitas/datasource/sensus/id/41/",
            {
                "kegiatan": kegiatan,
                "wilayah_sensus": wilayah_sensus,
                "dataset": dataset,
            },
        )

    # ================================================================
    # SIMDASI DATA
    # ================================================================

    def get_simdasi_provinces(self) -> list[dict]:
        """Get SIMDASI province MFD codes."""
        resp = self._request(
            f"{self.BASE_URL}/v1/api/interoperabilitas/datasource/simdasi/id/26/"
        )
        return self._extract_data(resp)

    def get_simdasi_regencies(self, parent: str) -> list[dict]:
        """Get SIMDASI regency codes by province."""
        resp = self._request(
            f"{self.BASE_URL}/v1/api/interoperabilitas/datasource/simdasi/id/27/",
            {"parent": parent},
        )
        return self._extract_data(resp)

    def get_simdasi_districts(self, parent: str) -> list[dict]:
        """Get SIMDASI district codes by regency."""
        resp = self._request(
            f"{self.BASE_URL}/v1/api/interoperabilitas/datasource/simdasi/id/28/",
            {"parent": parent},
        )
        return self._extract_data(resp)

    def get_simdasi_subjects(self, wilayah: str) -> list[dict]:
        """Get SIMDASI subjects for area."""
        resp = self._request(
            f"{self.BASE_URL}/v1/api/interoperabilitas/datasource/simdasi/id/22/",
            {"wilayah": wilayah},
        )
        return self._extract_data(resp)

    def get_simdasi_master_tables(self) -> list[dict]:
        """Get SIMDASI master tables."""
        resp = self._request(
            f"{self.BASE_URL}/v1/api/interoperabilitas/datasource/simdasi/id/34/"
        )
        return self._extract_data(resp)

    def get_simdasi_table_detail(
        self, wilayah: str, tahun: int, id_tabel: str
    ) -> dict:
        """Get SIMDASI table detail with data."""
        return self._request(
            f"{self.BASE_URL}/v1/api/interoperabilitas/datasource/simdasi/id/25/",
            {"wilayah": wilayah, "tahun": tahun, "id_tabel": id_tabel},
        )

    def get_simdasi_tables_by_area(self, wilayah: str) -> list[dict]:
        """Get SIMDASI tables based on area."""
        resp = self._request(
            f"{self.BASE_URL}/v1/api/interoperabilitas/datasource/simdasi/id/23/",
            {"wilayah": wilayah},
        )
        return self._extract_data(resp)

    def get_simdasi_tables_by_area_and_subject(
        self, wilayah: str, id_subjek: str
    ) -> list[dict]:
        """Get SIMDASI tables based on area and subject."""
        resp = self._request(
            f"{self.BASE_URL}/v1/api/interoperabilitas/datasource/simdasi/id/24/",
            {"wilayah": wilayah, "id_subjek": id_subjek},
        )
        return self._extract_data(resp)

    def get_simdasi_master_table_detail(self, id_tabel: str) -> dict:
        """Get detail of SIMDASI master table."""
        return self._request(
            f"{self.BASE_URL}/v1/api/interoperabilitas/datasource/simdasi/id/36/",
            {"id_tabel": id_tabel},
        )

    def get_kbki(
        self, year: int = 2020, page: int = 1, perpage: int = 10
    ) -> dict:
        """Get KBKI (Indonesian Standard Classification of Education)."""
        model = f"kbki{year}"
        return self._extract_paginated(
            self._list(model, "0000", page=page, perpage=perpage)
        )

    def get_kbki_detail(
        self, kbki_id: str, year: int = 2020, lang: str = "ind"
    ) -> dict:
        """Get KBKI classification detail."""
        model = f"kbki{year}"
        return self._view(model, kbki_id, "0000", lang)

    def search_generic(
        self, keyword: str, domain: str = "0000", lang: str = "ind", page: int = 1
    ) -> dict:
        """Generic search across BPS WebAPI."""
        return self._extract_paginated(
            self._list("search", domain, keyword=keyword, lang=lang, page=page)
        )


# ================================================================
# USAGE EXAMPLE
# ================================================================

if __name__ == "__main__":
    import os
    import sys

    # Get API key from environment variable
    app_id = os.getenv("WEBAPI_APP_ID")
    if not app_id:
        print("Error: WEBAPI_APP_ID environment variable is not set")
        print("Please set it with: export WEBAPI_APP_ID=your_api_key_here")
        sys.exit(1)
    
    api = BPSAPI(app_id)

    print("=== BPS API Client Demo ===\n")

    # Domains
    domains = api.get_domains()
    print(f"Total domains: {len(domains)}")

    provinces = api.get_provinces()
    print(f"Provinces: {len(provinces)}")

    # Subjects
    result = api.get_subjects()
    print(f"Subjects (page 1): {len(result['items'])}")

    # Publications
    pubs = api.get_publications(year=2024)
    print(f"Publications (2024): {pubs['pagination'].get('total', 0)}")

    # Press releases
    press = api.get_press_releases(year=2024)
    print(f"Press releases (2024): {press['pagination'].get('total', 0)}")

    # SDGs
    sdgs = api.get_sdgs(goal="1")
    print(f"SDGs Goal 1 indicators: {len(sdgs['items'])}")

    # Census
    census_events = api.get_census_events()
    print(f"Census events: {len(census_events)}")

    # SIMDASI
    simdasi_prov = api.get_simdasi_provinces()
    print(f"SIMDASI provinces: {len(simdasi_prov)}")

    print("\n=== Demo Complete ===")
