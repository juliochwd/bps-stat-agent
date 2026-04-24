"""Tests for BPS table parsing behavior."""

from mini_agent.bps_data_retriever import BPSDataRetriever


def make_retriever() -> BPSDataRetriever:
    """Create an instance without running API-key validation."""
    return object.__new__(BPSDataRetriever)


def test_parse_html_table_extracts_headers_and_rows_without_fixed_index():
    """Parser should find the first meaningful header row, not assume row index 3."""
    retriever = make_retriever()
    html = """
    <table>
      <tr><th colspan="2">Tabel Statistik</th></tr>
      <tr><th>Wilayah</th><th>Nilai</th></tr>
      <tr><td>Kupang</td><td>12,34</td></tr>
      <tr><td>Belu</td><td>56,78</td></tr>
    </table>
    """

    headers, rows = retriever._parse_html_table(html)

    assert headers == ["Wilayah", "Nilai"]
    assert rows == [["Kupang", "12,34"], ["Belu", "56,78"]]


def test_parse_html_table_normalizes_entities_and_whitespace():
    """Parser should normalize HTML entities and repeated whitespace."""
    retriever = make_retriever()
    html = """
    <table>
      <tr><th colspan="2">Ringkasan</th></tr>
      <tr><th>Komponen&nbsp;Utama</th><th>Satuan</th></tr>
      <tr><td>Inflasi &amp; Deflasi</td><td> persen </td></tr>
    </table>
    """

    headers, rows = retriever._parse_html_table(html)

    assert headers == ["Komponen Utama", "Satuan"]
    assert rows == [["Inflasi & Deflasi", "persen"]]


def test_parse_html_table_supports_excel_style_td_headers():
    """BPS static tables often encode headers with td cells from Excel exports."""
    retriever = make_retriever()
    html = """
    <table>
      <tr><td colspan="3">Inflasi Bulanan</td></tr>
      <tr><td>Bulan</td><td>Makanan</td><td>Transportasi</td></tr>
      <tr><td>Januari</td><td>1,23</td><td>0,45</td></tr>
      <tr><td>Februari</td><td>0,98</td><td>0,12</td></tr>
    </table>
    """

    headers, rows = retriever._parse_html_table(html)

    assert headers == ["Bulan", "Makanan", "Transportasi"]
    assert rows == [
        ["Januari", "1,23", "0,45"],
        ["Februari", "0,98", "0,12"],
    ]


def test_parse_html_table_handles_escaped_markup():
    """BPS WebAPI returns the table HTML escaped inside JSON."""
    retriever = make_retriever()
    html = (
        "&lt;table&gt;"
        "&lt;tr&gt;&lt;td colspan=&quot;3&quot;&gt;Inflasi Bulanan&lt;/td&gt;&lt;/tr&gt;"
        "&lt;tr&gt;&lt;td&gt;Bulan&lt;/td&gt;&lt;td&gt;Makanan&lt;/td&gt;&lt;td&gt;Transportasi&lt;/td&gt;&lt;/tr&gt;"
        "&lt;tr&gt;&lt;td&gt;Januari&lt;/td&gt;&lt;td&gt;1,23&lt;/td&gt;&lt;td&gt;0,45&lt;/td&gt;&lt;/tr&gt;"
        "&lt;/table&gt;"
    )

    headers, rows = retriever._parse_html_table(html)

    assert headers == ["Bulan", "Makanan", "Transportasi"]
    assert rows == [["Januari", "1,23", "0,45"]]
