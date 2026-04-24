
- [Homepage](#homepage)
- [Domain](#domain)
- [Subject](#subject)
- [Subject Categories](#subject-categories)
- [Dynamic Data](#dynamic-data)
- [Data](#data)
- [List Derived Period Data](#list-derived-period-data)
- [List Derived Variable](#list-derived-variable)
- [List Period Data](#list-period-data)
- [List Unit Data](#list-unit-data)
- [List Variable](#list-variable)
- [List Vertical Variable](#list-vertical-variable)
- [Census Data](#census-data)
- [SIMDASI](#simdasi)
- [Static Table](#static-table)
- [Detail Static Table](#detail-static-table)
- [List All Static Table](#list-all-static-table)
- [CSA Subject](#csa-subject)
- [Press Release](#press-release)
- [Detail Press Release](#detail-press-release)
- [List All Press Release](#list-all-press-release)
- [Publication](#publication)
- [Detail Publication](#detail-publication)
- [List All Publication](#list-all-publication)
- [Strategic Indicator](#strategic-indicator)
- [Infographic](#infographic)
- [Glosarium](#glosarium)
- [Foreign Trade Data](#foreign-trade-data)
- [Sustainable Development Goals](#sustainable-development-goals)
- [SDDS](#sdds)
- [Statistical Classifications](#statistical-classifications)
- [Searching](#searching)
- [News](#news)
- [Detail News](#detail-news)
- [List All BPS News](#list-all-bps-news)
- [List News Category](#list-news-category)
- [Badan Pusat Statistik](#badan-pusat-statistik)
- [API Documentation](#api-documentation)
- [The BPS APIs provides programmatic access to read BPS data. User can read about Publication, Press Release, BPS Event, and a lot of various kinds of data presented in the static table and dynamic tables. The BPS API identifies user with key token. User can get the key token from API-Portal website. Every user can get two until three key token to access the API. Responses are available in JSON.](#the-bps-apis-provides-programmatic-access-to-read-bps-data.-user-can-read-about-publication,-press-release,-bps-event,-and-a-lot-of-various-kinds-of-data-presented-in-the-static-table-and-dynamic-tables.-the-bps-api-identifies-user-with-key-token.-user-can-get-the-key-token-from-api-portal-website.-every-user-can-get-two-until-three-key-token-to-access-the-api.-responses-are-available-in-json.)




## Domain
This service is used to displays all BPS Statistics domain website



**Endpoint:** `https://webapi.bps.go.id/v1/api/domain`



### Parameter
Field	Type	Description
type	String	
Type to show domain (all:for all domain ; prov:for province domain ; kab:for city/regency domain ; kabbyprov:for all city/regency in province)

Allowed values: "all", "prov", "kab", "kabbyprov"

prov optional	String	
Prov ID selected to show all city/regency domain. input this parameter when using "kabbyprov" type.

Size range: 4

key	String	
Key app to access API



### Send a Sample Request




### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status of list domain.

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  1	Object	
List Domain

    domain_id	String	
ID domain

    domain_name	String	
name of domain

    domain_url	String	
URL domain




### Success Response
```http
HTTP/1.1 200 OK
            {
              "status": "OK",
              "data-availability": "available",
              "data":[{
              "page":1,
              "pages":1,
              "total":3
            },
            [{
            "domain_id":"0000",
            "domain_name":"Pusat",
            "domain_url":"https://www.bps.go.id"
          },{
          "domain_id":"1100",
          "domain_name":"Aceh",
          "domain_url":"https://aceh.bps.go.id"
        },{
        "domain_id":"1200",
        "domain_name":"Sumatera Utara",
        "domain_url":"https://sumut.bps.go.id",
      }]
      ]

    }
```



### Error 4xx
Name	Description
UserNotFound	
The id of the User was not found.




### Error Response
```http
HTTP/1.1 404 Not Found
      {
        "error": "UserNotFound"
      }
```



## Subject
List of All Subject
This service is used to displays all subject data on the website



**Endpoint:** `https://webapi.bps.go.id/v1/api/list/`



### Parameter
Field	Type	Description
model	String	
Model to display Subject Data (subject) for subject is "subject"

lang optional	String	
Language to display subject

Default value: ind

Allowed values: "ind", "eng"

domain	Number	
Domains that will be displayed subject (see master domain)

Allowed values: 4

subcat optional	Number	
Subject categories selected to display subject data

Allowed values: 1, 2, 3, 4, ..., n

page optional	Number	
Page to display subject

Allowed values: 1, 2, 3, 4, ..., n

key	String	
Key app to access API



### Send a Sample Request




### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status of list subject.

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  1	Object	
List subject

    sub_id	Number	
ID unique of subject

    title	String	
Title of subject

    subcat_id	String	
ID unique of sub category

    subcat	String	
Name of sub category

    ntable	Number	
Sum of table on each subject




### Success Response
```http
HTTP/1.1 200 OK
{
  "status": "OK",
  "data-availability": "available",
  "data": [
    {
      "page": 1,
      "pages": 5,
      "per_page": 10,
      "count": 10,
      "total": 48
    },
    [
      {
        "sub_id": 40,
        "title": "Gender",
        "subcat_id": 1,
        "subcat": "Sosial dan Kependudukan",
        "ntabel": null
      }, ...
    ]

}
```



### Error 4xx
Name	Description
UserNotFound	
The id of the User was not found.




### Error Response
```http
HTTP/1.1 404 Not Found
  {
    "error": "UserNotFound"
  }
```



## Subject Categories
List of All Subject Categories
This service is used to displays all subject data categories on the website



**Endpoint:** `https://webapi.bps.go.id/v1/api/list/`



### Parameter
Field	Type	Description
model	String	
Model to display Subject Categories (subcat) for subcat is "subcat"

lang optional	String	
Language to display subject category

Default value: ind

Allowed values: "ind", "eng"

domain	Number	
Domains that will be displayed subcat (see master domain)

Size range: 4

page optional	Number	
Page to display subcat

Allowed values: 1, 2, 3, 4, ..., n

key	String	
Key app to access API



### Send a Sample Request




### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status of list subcat.

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  1	Object	
List subcat

    subcat_id	Number	
ID unique of subcat

    title	String	
Title of subcat




### Success Response
```http
HTTP/1.1 200 OK
{
  "status": "OK",
  "data-availability": "available",
  "data": [
    {
      "page": 1,
      "pages": 1,
      "per_page": 10,
      "count": 4,
      "total": 4
    },
    [
      ...
      {
        "subcat_id": 1,
        "title": "Sosial dan Kependudukan"
      },
      ...
    ]
  ]
}
```



### Error 4xx
Name	Description
UserNotFound	
The id of the User was not found.




### Error Response
```http
HTTP/1.1 404 Not Found
  {
    "error": "UserNotFound"
  }
```



## Dynamic Data


## Data
This service is used to displays data of dynamic table in the website



**Endpoint:** `https://webapi.bps.go.id/v1/api/list`



### Parameter
Field	Type	Description
model	String	
Model to display Data for variable is "data"

lang optional	String	
Language to display data

Default value: ind

Allowed values: "ind", "eng"

domain	Number	
Domains that will be displayed variable (see master domain)

Size range: 4

var	Number	
Variable ID selected to display data

Allowed values: 1, 2, 3, 4, ..., n

turvar optional	Number	
Derived Variable ID selected to display data

Allowed values: 1, 2, 3, 4, ..., n

vervar optional	Number	
Vertical Variable ID selected to display data

Allowed values: 1, 2, 3, 4, ..., n

th	Number	
Period data ID selected to display data

Allowed values: 1, 2;3, 2:6

turth optional	Number	
Derived Period Data ID selected to display data

Allowed values: 1, 2;3, 2:6

key	String	
Key app to access API



### Send a Sample Request




### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status of list subject.

var	Number	
Variable ID

turvar	Number	
Derived Variable ID

labelvervar	Number	
Title of Vertical Variable

vervar	Number	
Vertical Variable ID

tahun	Number	
Period of Data

turtahun	Number	
Derived period data

datacontent	Object	


## Data




### Success Response
```http
HTTP/1.1 200 OK
{
  "status": "OK",
  "data-availability": "available",
  "var": [
    {
      "val": 145,
      "label": "Persentase Rumah Tangga Menurut Provinsi dan Sumber Penerangaan",
      "unit": "Persen",
      "subj": "Lingkungan Hidup",
      "def": "",
      "decimal": "",
      "note": "- Sumber: Diolah dari Hasil Survei Sosial Ekonomi Nasional (Susenas), BPS.\n<br>- Tahun 2000 Tidak termasuk Dista Aceh dan Maluku\n<br>- Tahun 2006 Tanpa kabupaten Bantul \n<br>-Data dikutip dari Publikasi Statistik Indonesia.\n"
    }
  ],
  "turvar": [
    {
      "val": 289,
      "label": "Listrik PLN"
    },
    ...
  ],
  "labelvervar": "Provinsi",
  "vervar": [
    {
      "val": 9999,
      "label": "INDONESIA"
    },
    ...
  ],
  "tahun": [
    {
      "val": 100,
      "label": "2000"
    },
    ...
  ],
  "turtahun": [
    {
      "val": 0,
      "label": "Tahun"
    },
    ...
  ],
  "metadata": {
    "activity": null,
    ...
  },
  "datacontent": {
    "99991452891000": 83.68,
    ...
  }
}
```



### Error 4xx
Name	Description
UserNotFound	
The id of the User was not found.




### Error Response
```http
HTTP/1.1 404 Not Found
    {
      "error": "UserNotFound"
    }
```



## List Derived Period Data
This service is used to displays all derived period data on dynamic table in the website



**Endpoint:** `https://webapi.bps.go.id/v1/api/list`



### Parameter
Field	Type	Description
model	String	
Model to display derived period data for derived period data is "turth"

lang optional	String	
Language to display derived period data

Default value: ind

Allowed values: "ind", "eng"

domain	Number	
Domains that will be displayed derived period data (see master domain)

Size range: 4

var optional	Number	
Variable ID selected to display derived period data

Allowed values: 1, 2, 3, 4, ..., n

page optional	Number	
Page to display derived period data

Allowed values: 1, 2, 3, 4, ..., n

key	String	
Key app to access API



### Send a Sample Request




### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status of list subject.

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  1	Object	
List subject

    turth_id	String	
ID unique of subject

    turth	String	
Title of subject

    group_turth_id	String	
ID unique of subject

    name_group_turth	String	
Title of subject




### Success Response
```http
HTTP/1.1 200 OK
      {
        "status": "OK",
        "data-availability": "available",
        "data":[{
        "page":1,
        "pages":230,
        "per_page":10,
        "count":10,
        "total":2300
      },
      [{
      "turth_id":0,
      "turth":"Tahun",
      "group_turth_id":0,
      "name_group_turth":"Tahunan"
    },{
    "turth_id":1,
    "turth":"Bulanan",
    "group_turth_id":1,
    "name_group_turth":"January"
  },{
  "turth_id":2,
  "turth":"Bulanan",
  "group_turth_id":2,
  "name_group_turth":"February"
}]
]

}
```



### Error 4xx
Name	Description
UserNotFound	
The id of the User was not found.




### Error Response
```http
HTTP/1.1 404 Not Found
  {
    "error": "UserNotFound"
  }
```



## List Derived Variable
This service is used to displays all derived variable on dynamic table in the website



**Endpoint:** `https://webapi.bps.go.id/v1/api/list`



### Parameter
Field	Type	Description
model	String	
Model to display derived variable for derived variable is "turvar"

lang optional	String	
Language to display derived variable

Default value: ind

Allowed values: "ind", "eng"

domain	Number	
Domains that will be displayed variable (see master domain)

Size range: 4

var optional	Number	
Variable selected to display derived variable

Allowed values: 1, 2, 3, 4, ..., n

group optional	Number	
Group Vertical Variable selected to display derived variable

Allowed values: 1, 2, 3, 4, ..., n

nopage optional	Boolean	
param to show with no pagination (1 if want to no pagination)

Allowed values: 0, 1

page optional	Number	
Page to display derived variable

Allowed values: 1, 2, 3, 4, ..., n

key	String	
Key app to access API



### Send a Sample Request




### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status of list derived variable.

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  1	Object	
List derived variable

    turvar_id	Number	
ID unique of derived variable

    turvar	String	
Title of derived variable

    group_turvar_id	Number	
ID unique of item group derived variable

    name_group_turvar	String	
Group Name of derived variable *




### Success Response
```http
HTTP/1.1 200 OK
{
  "status": "OK",
  "data-availability": "available",
  "data":[{
     "page":1,
     "pages":230,
     "per_page":10,
     "count":10,
     "total":2300
     },
     [{
         "turvar_id":3200,
         "turvar":"Title of vertical variable",
         "group_turvar_id":"Group Name",
         "name_group_turvar":"Wilayah Provinsi"
     },{
         "turvar_id":3200,
         "turvar":"Title of vertical variable",
         "group_turvar_id":"Group Name",
         "name_group_turvar":"Wilayah Provinsi"
     }]
  ]
    
}
```



### Error 4xx
Name	Description
UserNotFound	
The id of the User was not found.




### Error Response
```http
HTTP/1.1 404 Not Found
  {
    "error": "UserNotFound"
  }
```



## List Period Data
This service is used to displays all period data on dynamic table in the website



**Endpoint:** `https://webapi.bps.go.id/v1/api/list`



### Parameter
Field	Type	Description
model	String	
Model to display period data for variable is "th"

lang optional	String	
Language to display period data

Default value: ind

Allowed values: "ind", "eng"

domain	Number	
Domains that will be displayed variable (see master domain)

Size range: 4

var optional	Number	
Variable ID selected to display period data

Allowed values: 1, 2, 3, 4, ..., n

page optional	Number	
Page to display subject

Allowed values: 1, 2, 3, 4, ..., n

key	String	
Key app to access API



### Send a Sample Request




### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status of list subject.

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  1	Object	
List subject

    th_id	Number	
ID unique of period data

    th	String	
Title of period data




### Success Response
```http
HTTP/1.1 200 OK
{
  "status": "OK",
  "data-availability": "available",
  "data":[{
     "page":1,
     "pages":230,
     "per_page":10,
     "count":10,
     "total":2300
     },
     [{
         "th_id":117,
         "th":2017
     },{
         "th_id":116,
         "th":2016
     },{
         "th_id":115,
         "th":2015
     }]
  ]
    
}
```



### Error 4xx
Name	Description
UserNotFound	
The id of the User was not found.




### Error Response
```http
HTTP/1.1 404 Not Found
  {
    "error": "UserNotFound"
  }
```



## List Unit Data
This service is used to displays all unit data on dynamic table in the website



**Endpoint:** `https://webapi.bps.go.id/v1/api/list`



### Parameter
Field	Type	Description
model	String	
Model to display unit data for unit data is "unit"

lang optional	String	
Language to display unit data

Default value: ind

Allowed values: "ind", "eng"

domain	Number	
Domains that will be displayed unit data(see master domain)

Size range: 4

page optional	Number	
Page to display unit data

Allowed values: 1, 2, 3, 4, ..., n

key	String	
Key app to access API



### Send a Sample Request




### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status of list unit data.

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  1	Object	
List unit data

    unit_id	Number	
ID unique of unit data

    unit	String	
Title of unit data




### Success Response
```http
HTTP/1.1 200 OK
{
  "status": "OK",
  "data-availability": "available",
  "data":[{
     "page":1,
     "pages":230,
     "per_page":10,
     "count":10,
     "total":2300
     },
     [{
         "unit_id":45678,
         "unit":"Title of unit",
     },{
         "unit_id":45678,
         "unit":"Title of unit",
     }]
  ]
    
}
```



### Error 4xx
Name	Description
UserNotFound	
The id of the User was not found.




### Error Response
```http
HTTP/1.1 404 Not Found
  {
    "error": "UserNotFound"
  }
```



## List Variable
This service is used to displays all variable on dynamic table in the website



**Endpoint:** `https://webapi.bps.go.id/v1/api/list`



### Parameter
Field	Type	Description
model	String	
Model to display variable Data (subject) for variable is "var"

lang optional	String	
Language to display variable

Default value: ind

Allowed values: "ind", "eng"

domain	Number	
Domains that will be displayed variable (see master domain)

Allowed values: 4

subject optional	Number	
Subject ID selected to display subject data

Allowed values: 1, 2, 3, 4, ..., n

page optional	Number	
Page to display subject

Allowed values: 1, 2, 3, 4, ..., n

year optional	Number	
Year selected to display statictable

Allowed values: 1, 2, 3, 4, ..., n

area optional	Boolean	
Parameter to show exist variabel on domain (1 if show exist var)

Allowed values: 0, 1

vervar optional	Number	
Vertical Variabel ID selected

Allowed values: 1, 2, 3, 4, ..., n

key	String	
Key app to access API



### Send a Sample Request




### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status of list variable.

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  1	Object	
List variable

    var_id	Number	
ID unique of variable

    title	String	
Title of variable

    sub_id	Number	
ID unique of variable

    sub_name	String	
Title of variable

    def	String	
Definition of Variable

    notes	String	
Notes for Variable

    vertical	Number	
ID vertical variable

    unit	String	
Unit Metric

    graph_id	Number	
ID graph

    graph_name	String	
graph name




### Success Response
```http
HTTP/1.1 200 OK
{
  "status": "OK",
  "data-availability": "available",
  "data":[{
     "page":1,
     "pages":230,
     "per_page":10,
     "count":10,
     "total":2300
     },
     [{
         "var_id":45678,
         "title":"Title of variable",
         "sub_id":45,
         "sub_name":"Subject Name",
         "def":"definition",
         "notes":"notes",
         "vertical":3,
         "unit":"Billion",
         "graph_id":3,
         "graph_name":"Line",
     },{
          "var_id":458,
         "title":"Title of variable 2",
         "sub_id":45,
         "sub_name":"Subject Name",
         "def":"definition",
         "notes":"notes",
         "vertical":3,
         "unit":"Billion",
         "graph_id":3,
         "graph_name":"Line",
     }]
  ]
    
}
```



### Error 4xx
Name	Description
UserNotFound	
The id of the User was not found.




### Error Response
```http
HTTP/1.1 404 Not Found
  {
    "error": "UserNotFound"
  }
```



## List Vertical Variable
This service is used to displays all vertical variable on dynamic table in the website



**Endpoint:** `https://webapi.bps.go.id/v1/api/list`



### Parameter
Field	Type	Description
model	String	
Model to display vertical variable Data for vertical variable is "vervar"

lang optional	String	
Language to display vertical variable

Default value: ind

Allowed values: "ind", "eng"

domain	Number	
Domains that will be displayed variable (see master domain)

Allowed values: 4

var optional	Number	
Variable selected to display vertical variable

Allowed values: 1, 2, 3, 4, ..., n

page optional	Number	
Page to display vertical variable

Allowed values: 1, 2, 3, 4, ..., n

key	String	
Key app to access API



### Send a Sample Request




### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status of list vertical variable.

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  1	Object	
List vertical variable

    vervar_id	Number	
ID unique of vertical variable

    vervar	String	
Title of vertical variable

    item_ver_id	Number	
ID unique of item vertical variable

    group_ver_id	Number	
ID unique of Group vertical variable

    name_group_ver_id	String	
Group Name of vertical variable *




### Success Response
```http
HTTP/1.1 200 OK
{
  "status": "OK",
  "data-availability": "available",
  "data":[{
     "page":1,
     "pages":230,
     "per_page":10,
     "count":10,
     "total":2300
     },
     [{
         "vervar_id":3200,
         "vervar":"Title of vertical variable",
         "item_ver_id":45,
         "group_ver_id":"Group Name",
         "name_group_ver_id":"Wilayah Provinsi"
     },{
         "vervar_id":3200,
         "vervar":"Title of vertical variable",
         "item_ver_id":45,
         "group_ver_id":"Group Name",
         "name_group_ver_id":"Wilayah Provinsi"
     }]
  ]
    
}
```



### Error 4xx
Name	Description
UserNotFound	
The id of the User was not found.




### Error Response
```http
HTTP/1.1 404 Not Found
  {
    "error": "UserNotFound"
  }
```

Census Data (sensus.bps.go.id)


## List of Census Events
This service is used to return a list of events included in the Census Web



**Endpoint:** `https://webapi.bps.go.id/v1/api/interoperabilitas/datasource/sensus/id/37/`



### Parameter
Field	Type	Description
id	Number	
Id number of the service. To display a list of events that is included in the Census, use code 37.

key	String	
Key app to access API



### Send a Sample Request




### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status of events list

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  1	Object	
List events

    id	Number	
ID of Event

    kegiatan	String	
Name of Event

    tahun_kegiatan	Number	
Year of Event




### Success Response
```http
HTTP/1.1 200 OK
{
  "status": "OK",
  "data-availability": "available",
  "data": [
    {
      "page": 1,
      "pages": 1,
      "per_page": 1,
      "count": 1,
      "total": 1
    },
    [
      {
        "id": {{id of event}},
        "kegiatan": {{name of event}},
        "tahun_kegiatan": {{year of event}}
      },
     …
    ]
  ]
}
```



### Error 4xx
Field	Type	Description
Status	String	
Return status, OK if success and Error if any error occurred.

Data-availibility	String	
Availability status of events list




### Error Response

```json
{
  "status": "Error",
  "data-availability": "not-available",
  "data": [
    {
      "page": 1,
      "pages": 0,
      "per_page": 25,
      "count": 0,
      "total": 0
    },
    []
  ]
}
```



## Data Topics in the Census
This service is used to display the data topics available in the census that we choose.



**Endpoint:** `https://webapi.bps.go.id/v1/api/interoperabilitas/datasource/sensus/id/38/`



### Parameter
Field	Type	Description
id	Number	
Id number of the service. To display a list of data topics that is included in the Census, use code 38.

Kegiatan	String	
ID of census event that we choose to display the data topics, use service list of events to get the ID. Example: sp2020

key	String	
Key app to access API



### Send a Sample Request




### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status of Data Topics

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  1	Object	
List Data Topics

    id	Number	
ID of Data Topics

    topik	String	
Name of Data Topic in Bahasa

    topic	String	
Name of Data Topic in English

    id_kegiatan	Number	
ID of Events

    kegiatan	String	
Name of event in Bahasa

    event	String	
Name of event in English

    alias_kegiatan	String	
Alias of event in Bahasa

    alias_event	String	
Alias of event in English




### Success Response
```http
HTTP/1.1 200 OK
{
  "status": "OK",
  "data-availability": "available",
  "data": [
    {
      "page": 1,
      "pages": 1,
      "per_page": 1,
      "count": 1,
      "total": 1
    },
    [
      {
        "id": {{id of Data Topic}},
        "topik": {{name of Data topic in bahasa}},
        "topic": {{name of Data topic in english}},
        "id_kegiatan": {{Id of event}},
        "kegiatan": {{Name of event in Bahasa}},
        "event": {{Name of event in English}},
        "alias_kegiatan": {{Alias of event in Bahasa}},
        "alias_event": {{Alias of event in English}}
      }
    ]
  ]
}
```




### Error 4xx
Field	Type	Description
Status	String	
Return status, OK if success and Error if any error occurred.

Data-availibility	String	
Availability status of data topics




### Error Response

```json
{
  "status": "Error",
  "data-availability": "not-available",
  "data": [
    {
      "page": 1,
      "pages": 0,
      "per_page": 25,
      "count": 0,
      "total": 0
    },
    []
  ]
}
```



## List of Census Event Areas
This service is used to return a list of areas in the Census Event



**Endpoint:** `https://webapi.bps.go.id/v1/api/interoperabilitas/datasource/sensus/id/38/`



### Parameter
Field	Type	Description
id	Number	Id number of the service. To display a list of census event areas, use code 39.
Kegiatan	String	
ID of census event that we choose to display the census event areas, use service list of events to get the ID. Example: sp2020

key	String	
Key app to access API



### Send a Sample Request




### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status of Census Event Area

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  1	Object	
List of Area

    id	Number	
ID of area

    kode_mfd	String	
MFD Code of area

    nama	String	
Name of area

    slug	String	
-




### Success Response
```http
HTTP/1.1 200 OK
{
  "status": "OK",
  "data-availability": "available",
  "data": [
    {
      "page": 1,
      "pages": 1,
      "per_page": 1,
      "count": 1,
      "total": 1
    },
    [
      {
        "id": {{ ID of Census Event Area}},
        "kode_mfd": {{ MFD CODE}},
        "nama": {{ Name of area }},
        "slug": -
      },


```

### Error 4xx
Field	Type	Description
Status	String	
Return status, OK if success and Error if any error occurred.

Data-availibility	String	
Availability status of census event area



### Error Response

```json
{
  "status": "Error",
  "data-availability": "not-available",
  "data": [
    {
      "page": 1,
      "pages": 0,
      "per_page": 25,
      "count": 0,
      "total": 0
    },
    []
  ]
}
```

List of Available Dataset based on Event and Data Topic
This service is used to return a list of events included in the Census


**Endpoint:** `https://webapi.bps.go.id/v1/api/interoperabilitas/datasource/sensus/id/40/`


### Parameter
Field	Type	Description
id	Number	Id number of the service. To display a list of available dataset, use code 40.
Kegiatan	String	
ID of census event that we choose to display the census dataset, use service list of events to get the ID. Example: sp2020

Topik	Number	
ID of Data topic, use service list of data topics to get the ID.

key	String	
Key app to access API


### Send a Sample Request



### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status of Dataset

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  1	Object	
List of Dataset

    id	Number	
ID of dataset

    id_topik	Number	
ID of data topic

    topic	String	
Name of data topic

    id_kegiatan	Number	
ID of census event

    Nama	String	
Name of dataset

    deskripsi	String	
Description of dataset



### Success Response
```http
HTTP/1.1 200 OK
{
  "status": "OK",
  "data-availability": "available",
  "data": [
    {
      "page": 1,
      "pages": 1,
      "per_page": 1,
      "count": 1,
      "total": 1
    },
    [
      {
        "id": {{ Id of dataset }},
        "id_topik": {{ Id of data topic }},
        "topik": {{ Name of data topic }},
        "id_kegiatan": {{ Id of Census Event }},
        "nama": {{ Name of dataset }},
        "deskripsi": {{ Description of dataset }}
      }
 ]
}
```




### Error 4xx
Field	Type	Description
Status	String	
Return status, OK if success and Error if any error occurred.

Data-availibility	String	
Availability status of dataset



### Error Response

```json
{
  "status": "Error",
  "data-availability": "not-available",
  "data": [
    {
      "page": 1,
      "pages": 0,
      "per_page": 25,
      "count": 0,
      "total": 0
    },
    []
  ]
}
```


## Census Data
This service is used to return census data


**Endpoint:** `https://webapi.bps.go.id/v1/api/interoperabilitas/datasource/sensus/id/41/`


### Parameter
Field	Type	Description
id	Number	Id number of the service. To display census data based on ID of Census Event, Id of Census Area, and ID of Dataset, use code 41.
Kegiatan	String	
ID of census event that we choose to display the census dataset, use service list of events to get the ID. Example: sp2020

Wilayah_sensus	Number	
ID of Census Event Area, use service list of census event area to get the ID.

Dataset	Number	
ID of Dataset, use service list of census dataset to get the ID.

key	String	
Key app to access API


### Send a Sample Request



### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status of Data

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  1	Object	
Data Details

    timestamp	date	
Last Sync

    status	String	
Status of availability

    data_count	String	
Count of the data

    data	object[]	
Data content

      id_wilayah	number	
ID of area

      kode_wilayah	number	
Area code

      nama_wilayah	string	
Name of area

      level_wilayah	number	
Administration level of area

      id_indikator	number	
ID of indicator

      nama_indikator	number	
Name of indikator

      id_kategori_x	number	
ID of indicator x-th category

      name_kategori_x	string	
Name of indicator x-th category

      id_item_kategori_x	number	
ID of indicator x-th category item

      kode_item_kategori_x	number	
Code of indicator x-th category item

      nama_item_kategori_x	string	
Name of indicator x-th category item

      Period	number	
Year of indicator

      nilai	number	
Value of indicator



### Success Response
```http
HTTP/1.1 200 OK

  "status": "OK",
  "data-availability": "available",
  "data": [
    {
      "page": 1,
      "pages": 1,
      "per_page": 1,
      "count": 1,
      "total": 1
    },
```
```json
    {
      "timestamp": "2022-07-11T10:35:03.125",
      "status": 200,
      "data_count": 315,
      "data": [
        {
          "id_wilayah": "8f42c43e-051c-482b-84cf-285bc4606075",
          "kode_wilayah": "11",
          "nama_wilayah": "ACEH",
          "level_wilayah": 1,
          "id_indikator": "4700ed90-4a9a-46a4-9ccf-54ee556e2691",
          "nama_indikator": "Jumlah Penduduk Menurut Wilayah, Kesesuaian Alamat KK/KTP dengan Tempat Tinggal, dan Jenis Kelamin",
          "id_kategori_1": "d1332a64-cca8-4cdf-84e6-c79ca1e66910",
          "nama_kategori_1": "Klasifikasi Kesesuaian Alamat KK-KTP 2020",
          "id_item_kategori_1": "982b2f23-92bc-4fdc-83ea-2ebdfd478c52",
          "kode_item_kategori_1": "1",
          "nama_item__kategori_1": "Ya",
          "id_kategori_2": "05996fef-eaba-43ba-a917-c41108eaac6c",
          "nama_kategori_2": "Klasifikasi Jenis Kelamin 2010",
          "id_item_kategori_2": "3fccb669-2819-483a-8cb4-19b6aea53fe4",
          "kode_item_kategori_2": "L",
          "nama_item__kategori_2": "Laki-laki",
          "id_kategori_3": "",
          "nama_kategori_3": "",
          "id_item_kategori_3": "",
          "kode_item_kategori_3": "",
          "nama_item__kategori_3": "",
          "id_kategori_4": "",
          "nama_kategori_4": "",
          "id_item_kategori_4": "",
          "kode_item_kategori_4": "",
          "nama_item__kategori_4": "",
          "period": "2020",
          "nilai": "2523198.0"
        },
]


```

### Error 4xx
Field	Type	Description
Status	String	
Return status, OK if success and Error if any error occurred.

Data-availibility	String	
Availability status of data



### Error Response

```json
{
  "status": "Error",
  "data-availability": "not-available",
  "data": [
    {
      "page": 1,
      "pages": 0,
      "per_page": 25,
      "count": 0,
      "total": 0
    },
    []
  ]
}
```

SIMDASI (Sistem Informasi Manajemen Data Statistik Terintegrasi)
Indonesian Statistics (SI) and Regional In Numbers (DDA) publications are BPS-issued publications that are of interest and attention by the public. At the moment the publication is available at www.bps.go.id. BPS continues to strive to improve the quality of SI and DDA through the Integrated Statistical Data Management Information System (SIMDASI).

List of 7 Digit MFD Code of Province
This service used to view the 7 Digit MFD Code of Province that is used in wilayah parameter in other SIMDASI WebAPI Parameter


**Endpoint:** `https://webapi.bps.go.id/v1/api/interoperabilitas/datasource/simdasi/id/26/`


### Parameter
Field	Type	Description
key	String	
Key app to access API


### Send a Sample Request


List of 7 Digit MFD Code of Regency
This service used to view the 7 Digit MFD Code of Regency that is used in wilayah parameter in other SIMDASI WebAPI Parameter


**Endpoint:** `https://webapi.bps.go.id/v1/api/interoperabilitas/datasource/simdasi/id/27/`


### Parameter
Field	Type	Description
parent	String	
7 Digit MFD code of Province, use service List of 7 Digit MFD Code of Province to get the code

key	String	
Key app to access API


### Send a Sample Request


List of 7 Digit MFD Code of District
This service used to view the 7 Digit MFD Code of District that is used in wilayah parameter in other SIMDASI WebAPI Parameter


**Endpoint:** `https://webapi.bps.go.id/v1/api/interoperabilitas/datasource/simdasi/id/28/`


### Parameter
Field	Type	Description
parent	String	
7 Digit MFD code of Regency, use service List of 7 Digit MFD Code of Regency to get the code

key	String	
Key app to access API


### Send a Sample Request


List of SIMDASI Subject
This service used to view a list of subjects or chapters used in SIMDASI


**Endpoint:** `https://webapi.bps.go.id/v1/api/interoperabilitas/datasource/simdasi/id/22/`


### Parameter
Field	Type	Description
wilayah	String	
7 digit MFD Code of Area. Example for DKI Jakarta use 3100000

key	String	
Key app to access API


### Send a Sample Request



### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  1	Object	
Object

  data	Object	
List of subject

    id	String	
ID unique of subject

    bab	String	
Name of chapter in bahasa

    bab_en	String	
Name of chapter in english

    subject	String	
Name of subject in bahasa

    subject_en	String	
Name of subject in english

    mms_id	Number	
MMS ID of subject. This ID may be used in other endpoint as parameter of ID Subject. (MMS - Metadata Management system)

    mms_subject	String	
CSA Subject name that is used in MMS

    tabel	Object	
List of ID Table in this subject



### Success Response

```http
HTTP/1.1 200 OK
{
  "status": "OK",
  "data-availability": "available",
  "data": [
    {
      "page": 1,
      "pages": 1,
      "per_page": 1,
      "count": 1,
      "total": 1
    },
    {
      "status": 200,
      "condition": "OK",
      "message": "-",
      "created": "2022-08-01 11:33:33",
      "induk": "0000000",
      "wilayah": "Indonesia",
      "data": [
        {
          "id_tabel": "UFpWMmJZOVZlZTJnc1pXaHhDV1hPQT09",
          "judul": "Luas Daerah dan Jumlah Pulau Menurut Provinsi",
          "judul_en": "Total Area and Number of Islands by Province",
          "kode_tabel": "1.1.1",
          "ketersediaan_tahun": [
            2015,
            2016,
            2017,
            2018,
            2019,
            2021
          ],
          "id_subject": "OTJzVUFuRkhLQU1iTTVJUnM5Zko3QT09",
          "bab": "Geografi dan Iklim",
          "bab_en": "Geography and Climate",
          "subject": "Keadaan Geografi",
          "subject_en": "Geography Condition",
          "mms_id": 516,
          "mms_subject": "Statistik Lingkungan Hidup Dan Multi-domain"
        },

SIMDASI Master Table
This service used to view the Master Table that is used in SIMDASI

https://webapi.bps.go.id/v1/api/interoperabilitas/datasource/simdasi/id/34/

```

### Parameter
Field	Type	Description
key	String	
Key app to access API


### Send a Sample Request


Detail of SIMDASI Master Table
This service used to view the Detail of Master Table that is used in SIMDASI


**Endpoint:** `https://webapi.bps.go.id/v1/api/interoperabilitas/datasource/simdasi/id/36/`


### Parameter
Field	Type	Description
id_tabel	String	
ID of the Table

key	String	
Key app to access API


### Send a Sample Request


List of SIMDASI Table Based on Area
This service used to view a list of SIMDASI Table based on Area


**Endpoint:** `https://webapi.bps.go.id/v1/api/interoperabilitas/datasource/simdasi/id/23/`


### Parameter
Field	Type	Description
wilayah	String	
7 digit MFD Code of Area. Example for DKI Jakarta use 3100000

key	String	
Key app to access API


### Send a Sample Request



### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  1	Object	
Object

  data	Object	
List of subject

    id_tabel	String	
ID unique of table

    judul	String	
Table title in bahasa

    judul_en	String	
Table title in english

    kode_tabel	String	
Table code in SIMDASI

    ketersediaan_tahun	String	
Year availability of table

    id_subject	String	
ID unique of subject

    bab	String	
Name of chapter in bahasa

    bab_en	String	
Name of chapter in english

    subject	String	
Name of subject in bahasa

    subject_en	String	
Name of subject in english

    mms_id	Number	
MMS ID of subject. This ID may be used in other endpoint as parameter of ID Subject. (MMS - Metadata Management system)

    mms_subject	String	
CSA Subject name that is used in MMS

    tabel	Object	
List of ID Table in this subject



### Success Response

```http
HTTP/1.1 200 OK
{
  "status": "OK",
  "data-availability": "available",
  "data": [
    {
      "page": 1,
      "pages": 1,
      "per_page": 1,
      "count": 1,
      "total": 1
    },
    {
      "status": 200,
      "condition": "OK",
      "message": "-",
      "created": "2022-08-01 11:15:20",
      "induk": "0000000",
      "wilayah": "Indonesia",
      "data": [
        {
          "id_tabel": "UFpWMmJZOVZlZTJnc1pXaHhDV1hPQT09",
          "judul": "Luas Daerah dan Jumlah Pulau Menurut Provinsi",
          "judul_en": "Total Area and Number of Islands by Province",
          "kode_tabel": "1.1.1",
          "ketersediaan_tahun": [
            2015,
            2016,
            2017,
            2018,
            2019,
            2021
          ],
          "id_subject": "OTJzVUFuRkhLQU1iTTVJUnM5Zko3QT09",
          "bab": "Geografi dan Iklim",
          "bab_en": "Geography and Climate",
          "subject": "Keadaan Geografi",
          "subject_en": "Geography Condition",
          "mms_id": 516,
          "mms_subject": "Statistik Lingkungan Hidup Dan Multi-domain"
        },

List of SIMDASI Table Based on Area and Subject
This service used to view a list of SIMDASI Table based on Area and Subject

https://webapi.bps.go.id/v1/api/interoperabilitas/datasource/simdasi/id/24/

```

### Parameter
Field	Type	Description
wilayah	String	
7 digit MFD Code of Area. Example for DKI Jakarta use 3100000

id_subjek	String	
MMS_id of subject, use List of SIMDASI Subject to get the ID

key	String	
Key app to access API


### Send a Sample Request



### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  1	Object	
Object

  data	Object	
List of subject

    id_tabel	String	
ID unique of table

    judul	String	
Table title in bahasa

    judul_en	String	
Table title in english

    kode_tabel	String	
Table code in SIMDASI

    ketersediaan_tahun	String	
Year availability of table

    id_subject	String	
ID unique of subject

    bab	String	
Name of chapter in bahasa

    bab_en	String	
Name of chapter in english

    subject	String	
Name of subject in bahasa

    subject_en	String	
Name of subject in english

    mms_id	Number	
MMS ID of subject. This ID may be used in other endpoint as parameter of ID Subject. (MMS - Metadata Management system)

    mms_subject	String	
CSA Subject name that is used in MMS

    tabel	Object	
List of ID Table in this subject



### Success Response

```http
HTTP/1.1 200 OK
{
  "status": "OK",
  "data-availability": "available",
  "data": [
    {
      "page": 1,
      "pages": 1,
      "per_page": 1,
      "count": 1,
      "total": 1
    },
    {
      "status": 200,
      "condition": "OK",
      "message": "-",
      "created": "2022-08-01 11:15:20",
      "induk": "0000000",
      "wilayah": "Indonesia",
      "data": [
        {
          "id_tabel": "UFpWMmJZOVZlZTJnc1pXaHhDV1hPQT09",
          "judul": "Luas Daerah dan Jumlah Pulau Menurut Provinsi",
          "judul_en": "Total Area and Number of Islands by Province",
          "kode_tabel": "1.1.1",
          "ketersediaan_tahun": [
            2015,
            2016,
            2017,
            2018,
            2019,
            2021
          ],
          "id_subject": "OTJzVUFuRkhLQU1iTTVJUnM5Zko3QT09",
          "bab": "Geografi dan Iklim",
          "bab_en": "Geography and Climate",
          "subject": "Keadaan Geografi",
          "subject_en": "Geography Condition",
          "mms_id": 516,
          "mms_subject": "Statistik Lingkungan Hidup Dan Multi-domain"
        },

Detail of SIMDASI Table
This service used to view the detail of SIMDASI Table

https://webapi.bps.go.id/v1/api/interoperabilitas/datasource/simdasi/id/25/

```

### Parameter
Field	Type	Description
wilayah	String	
7 digit MFD Code of Area. Example for DKI Jakarta use 3100000

Tahun	Number	
Year of the Data

id_tabel	String	
id_tabel of table, use List of SIMDASI Table to get the ID

key	String	
Key app to access API


### Send a Sample Request



## Static Table
Detail Statictable
This service is used to displays detail of a statictable are shown on the website


**Endpoint:** `https://webapi.bps.go.id/v1/view`


### Parameter
Field	Type	Description
domain	Number	
Domains that will be displayed statictable (see master domain)

Size range: 4

model	String	
Model to display statictable (statictable) for statictable is "statictable"

lang	String	
Language to display static table

Default value: ind

Allowed values: "ind", "eng"

id	Number	
statictable id to display

Allowed values: 1, 2, 3, 4, ..., n

key	String	
Key app to access API


### Send a Sample Request



### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status of list statictable.

data	Object	
Information status

  table_id	Number	
ID unique of statictable

  subj_id	Number	
ID subject of statictable

  title	String	
Title of statictable

  table	String	
Title of statictable

  cr_date	String	
Create Date of statictable

  updt_date	String	
Update Date of statictable

  size	String	
File size of statictable

  excel	String	
Path location of statictable



### Success Response
```http
HTTP/1.1 200 OK
{
  "status": "OK",
  "data-availability": "available",
  "data":{
           "table_id": 111,
           "subj_id": 23,
           "title": "Inflasi data",
           "table": "sample html table",
           "cr_date": "2017-02-24",
           "updt_date": "2017-02-24",
           "excel": "http://jabar-dev.bps.go.id/new/website/tabelExcelIndo/Indo_23_3273895.xls",
           "size": " MB"
     }         
}
```


### Error 4xx
Name	Description
UserNotFound	
The id of the User was not found.



### Error Response
```http
HTTP/1.1 404 Not Found
  {
    "error": "UserNotFound"
  }
```


## List All Static Table
This service is used to displays all static table are shown on the website


**Endpoint:** `https://webapi.bps.go.id/v1/api/list/`


### Parameter
Field	Type	Description
model	String	
Model to display statictable (statictable) for statictable is "statictable"

lang optional	String	
Language to display static table

Default value: ind

Allowed values: "ind", "eng"

domain	Number	
Domains that will be displayed statictable (see master domain)

Size range: 4

page optional	Number	
Page to display statictable

Allowed values: 1, 2, 3, 4, ..., n

month optional	Number	
Month selected to display statictable

Allowed values: 1, 2, 3, 4, ..., n

year optional	Number	
Year selected to display statictable

Allowed values: 1, 2, 3, 4, ..., n

keyword optional	String	
Keyword to search

key	String	
Key app to access API


### Send a Sample Request



### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status of list statictable.

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  1	Object	
List statictable

    table_id	Number	
ID unique of statictable

    title	String	
Title of statictable

    subj_id	Number	
ID subject of statictable

    subj	String	
Subject of statictable

    updt_date	String	
Update Date of statictable

    size	String	
File size of statictable

    excel	String	
Path location of statictable



### Success Response
```http
HTTP/1.1 200 OK
      {
        "status": "OK",
        "data-availability": "available",
        "data":[{
        "page":1,
        "pages":230,
        "per_page":10,
        "count":10,
        "total":2300
      },
      [{
      "turth_id":0,
      "turth":"Tahun",
      "group_turth_id":0,
      "name_group_turth":"Tahunan"
    },{
    "turth_id":1,
    "turth":"Bulanan",
    "group_turth_id":1,
    "name_group_turth":"January"
  },{
  "turth_id":2,
  "turth":"Bulanan",
  "group_turth_id":2,
  "name_group_turth":"February"
}]
]

}
```


### Error 4xx
Name	Description
UserNotFound	
The id of the User was not found.



### Error Response
```http
HTTP/1.1 404 Not Found
  {
    "error": "UserNotFound"
  }
```

CSA Subject (Classification of Statistical Activities)
CSA (Classification of Statistical Activities) was established in 2005, used as the basis for providing information in the international statistical activities database currently managed by the Conference of European Statistics (CES). In the future, BPS will adopt the CSA Subject in the new website user interface design.

CSA Subject Categories
This service is used to show list of CSA subject categories


**Endpoint:** `https://webapi.bps.go.id/v1/api/list`


### Parameter
Field	Type	Description
domain	Number	
Domains that will be displayed pressrelease (see master domain)

Size range: 4

model	String	
Model to display CSA Subject Categories is "subcatcsa"

key	String	
Key app to access API


### Send a Sample Request



### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  1	Object	
Data List

    subcat_id	Number	
ID unique of CSA Subject Categories

    title	String	
Title of CSA Subject Categories



### Success Response
```http
HTTP/1.1 200 OK
{
  "status": "OK",
  "data-availability": "available",
  "data": [
    {
      "page": 1,
      "pages": 1,
      "per_page": 10,
      "count": 3,
      "total": 3
    },
    [
      {
        "subcat_id": 514,
        "title": "statistik demografi dan sosial"
      },
      {
        "subcat_id": 515,
        "title": "statistik ekonomi\n"
      },
      {
        "subcat_id": 516,
        "title": "statistik lingkungan hidup dan multi-domain"
      }
    ]
  ]
}
```


### Error 4xx
Name	Description
UserNotFound	
The id of the User was not found.



### Error Response
```http
HTTP/1.1 404 Not Found
  {
    "error": "UserNotFound"
  }
```


## CSA Subject
This service is used to show list of CSA subject


**Endpoint:** `https://webapi.bps.go.id/v1/api/list`


### Parameter
Field	Type	Description
domain	Number	
Domains that will be displayed pressrelease (see master domain)

Size range: 4

model	String	
Model to display CSA Subject is "subjectcsa"

subcat optional	String	
CSA Subject Categories ID, use service "CSA Subject Categories" to get the "subcat_id"

key	String	
Key app to access API


### Send a Sample Request



### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  1	Object	
Data List

    sub_id	Number	
ID unique of CSA Subject

    title	String	
Title of CSA Subject

    subcat_id	Number	
ID unique of CSA Subject Categories

    subcat	String	
Title of CSA Subject Categories



### Success Response
```http
HTTP/1.1 200 OK
{
  "status": "OK",
  "data-availability": "available",
  "data": [
    {
      "page": 1,
      "pages": 2,
      "per_page": 10,
      "count": 10,
      "total": 11
    },
    [
      {
        "sub_id": 528,
        "title": "Aktivitas Politik dan Komunitas Lainnya",
        "subcat_id": 514,
        "subcat": "statistik demografi dan sosial"
      },
    ]
  ]
}
```


### Error 4xx
Name	Description
UserNotFound	
The id of the User was not found.



### Error Response
```http
HTTP/1.1 404 Not Found
  {
    "error": "UserNotFound"
  }
```

List of Table (Using CSA Subject)
This service is used to show list of table that adopt the CSA Subject


**Endpoint:** `https://webapi.bps.go.id/v1/api/list`


### Parameter
Field	Type	Description
domain	Number	
Domains that will be displayed pressrelease (see master domain)

Size range: 4

model	String	
Model to display List of Table is "tablestatistic"

subject optional	Number	
CSA Subject ID, use service "CSA Subject" to get the "sub_id"

page optional	Number	
Page to display subject

Allowed values: 1, 2, 3, 4, ..., n

perpage optional	Number	
Sum of Table to display per page

Allowed values: 1, 2, 3, 4, ..., n

key	String	
Key app to access API


### Send a Sample Request



### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  1	Object	
Data List

    id	String	
ID unique of table

    title	String	
Title of Table

    id_subject	Number	
ID unique of CSA Subject

    subject	String	
Title of CSA Subject

    id_subcat	Number	
ID unique of CSA Subject Categories

    subcat	String	
Title of CSA Subject Categories

    tablesource	String	
Source of Table

1: Static Table

2: Dynamic Table

3: SIMDASI

Detail of Table (Using CSA Subject)
This service is used to show detail of table that adopt the CSA Subject


**Endpoint:** `https://webapi.bps.go.id/v1/api/view`


### Parameter
Field	Type	Description
domain	Number	
Domains that will be displayed pressrelease (see master domain)

Size range: 4

model	String	
Model to display List of Table is "tablestatistic"

id	String	
ID of table, use service "List of table" above to get the "id"

year optional	integer	
a four-digit year value between oldest_period and latest_period

lang	Number	
Language to display

Allowed values: "ind", "eng"

key	String	
Key app to access API


### Send a Sample Request



## Press Release

## Detail Press Release
This service is used to displays detail of a pressrelease are shown on the website


**Endpoint:** `https://webapi.bps.go.id/v1/view`


### Parameter
Field	Type	Description
domain	Number	
Domains that will be displayed pressrelease (see master domain)

Size range: 4

model	String	
Model to display pressrelease (pressrelease) for pressrelease is "pressrelease"

lang	String	
Language to display pressrelease

Allowed values: "ind", "eng"

id	Number	
pressrelease id to display

Allowed values: 1, 2, 3, 4, ..., n

key	String	
Key app to access API


### Send a Sample Request



### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status of list pressrelease.

data	Object	
Information status

  brs_id	Number	
ID unique of pressrelease

  title	String	
Title of pressrelease

  abstract	String	
Abstract of pressrelease

  rl_date	String	
Release Date of pressrelease

  updt_date	String	
Updated Date of pressrelease if any updated/revised pressrelease

  pdf	String	
Path Location of pressrelease File

  size	String	
Size File of pressrelease



### Success Response
```http
HTTP/1.1 200 OK
{
  "status": "OK",
  "data-availability": "available",
  "data":{
         "brs_id":"brs-f12345512",
         "title": "Title of pressrelease",
         "abstract":"Abstract of Press Release",
         "rl_date": "2016-10-08",
         "updt_date": null,
         "pdf": "path",
         "size": "1.2 MB",
     }         
}
```


### Error 4xx
Name	Description
UserNotFound	
The id of the User was not found.



### Error Response
```http
HTTP/1.1 404 Not Found
  {
    "error": "UserNotFound"
  }
```


## List All Press Release
This service is used to displays all press release are shown on the website


**Endpoint:** `https://webapi.bps.go.id/v1/api/list`


### Parameter
Field	Type	Description
model	String	
Model to display pressrelease (pressrelease) for pressrelease is "pressrelease"

lang optional	String	
Language to display pressrelease

Default value: ind

Allowed values: "ind", "eng"

domain	Number	
Domains that will be displayed pressrelease (see master domain)

Size range: 4

page optional	Number	
Page to display pressrelease

Allowed values: 1, 2, 3, 4, ..., n

month optional	Number	
Month selected to display pressrelease

Allowed values: 1, 2, 3, 4, ..., n

year optional	Number	
Year selected to display pressrelease

Allowed values: 1, 2, 3, 4, ..., n

keyword optional	String	
Keyword to search

key	String	
Key app to access API


### Send a Sample Request



### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status of list pressrelease.

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  1	Object	
List pressrelease

    brs_id	Number	
ID unique of pressrelease

    title	String	
Title of pressrelease

    rl_date	String	
Release Date of pressrelease

    updt_date	String	
Updated Date of pressrelease if any updated/revised pressrelease

    pdf	String	
Path Location of pressrelease File

    size	String	
Size File of pressrelease



### Success Response
```http
HTTP/1.1 200 OK
{
  "status": "OK",
  "data-availability": "available",
  "data":[{
     "page":1,
     "pages":230,
     "per_page":10,
     "count":10,
     "total":2300
     },
     [{
         "brs_id":"brs-13342312",
         "title": "Title of pressrelease",
         "rl_date": "2016-07-08",
         "updt_date": null,
         "pdf": "path",
         "size": "2.1 MB",
     },{
        "brs_id":"brs-13344512",
         "title": "Title of pressrelease now",
         "rl_date": "2016-07-08",
         "updt_date": null,
         "pdf": "path",
         "size": "2 MB",
     }]
  ]
    
}
```


### Error 4xx
Name	Description
UserNotFound	
The id of the User was not found.



### Error Response
```http
HTTP/1.1 404 Not Found
  {
    "error": "UserNotFound"
  }
```


## Publication

## Detail Publication
This service is used to displays detail of a publication are shown on the website


**Endpoint:** `https://webapi.bps.go.id/v1/view`


### Parameter
Field	Type	Description
domain	Number	
Domains that will be displayed publication (see master domain)

Size range: 4

model	String	
Model to display publication (publication) for publication is "publication"

lang	String	
Language to display publication

Allowed values: "ind", "eng"

id	String	
Publication id to display

key	String	
Key app to access API


### Send a Sample Request



### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status of list publication.

data	Object	
Information status

  pub_id	Number	
ID unique of Publication

  title	String	
Title of Publication

  kat_no	String	
Category Number of Publication

  pub_no	String	
Publication Number of Publication

  issn	String	
ISSN/ISBN number of Publication

  abstract	String	
Abstract of Publication

  sch_date	String	
Schedule Date of Publication

  rl_date	String	
Release Date of Publication

  updt_date	String	
Updated Date of Publication if any updated/revised publication

  cover	String	
Path Location of Publication cover

  pdf	String	
Path Location of Publication File

  size	String	
Size File of Publication



### Success Response
```http
HTTP/1.1 200 OK
{
  "status": "OK",
  "data-availability": "available",
  "data":{
         "pub_id":"pub-13342312",
         "title": "Title of Publication",
         "kat_no": "1212 1212 314",
         "pub_no": "1221",
         "issn": "0215-2169",
         "abstract": "Abstract of Publication",
         "sch_date": "2016-07-08",
         "rl_date": "2016-07-08",
         "updt_date": null,
         "cover": "path",
         "pdf": "path",
         "size": "21 MB",
     }         
}
```


### Error 4xx
Name	Description
UserNotFound	
The id of the User was not found.



### Error Response
```http
HTTP/1.1 404 Not Found
  {
    "error": "UserNotFound"
  }
```


## List All Publication
This service is used to displays all publication that are shown on the website


**Endpoint:** `https://webapi.bps.go.id/v1/api/list/`


### Parameter
Field	Type	Description
model	String	
Model to display publication (publication) for publication is "publication"

lang optional	String	
Language to display publication

Default value: ind

Allowed values: "ind", "eng"

domain	Number	
Domains that will be displayed publication (see master domain)

Size range: 4

page optional	Number	
Page to display publication

Allowed values: 1, 2, 3, 4, ..., n

month optional	Number	
Month selected to display publication

Allowed values: 1, 2, 3, 4, ..., n

year optional	Number	
Year selected to display publication

Allowed values: 1, 2, 3, 4, ..., n

keyword optional	String	
Keyword to search

key	String	
Key app to access API


### Send a Sample Request



### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status of list publication.

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  1	Object	
List publication

    pub_id	Number	
ID unique of Publication

    title	String	
Title of Publication

    issn	String	
ISSN/ISBN number of publication

    sch_date	String	
Schedule Date of Publication

    rl_date	String	
Release Date of Publication

    updt_date	String	
Updated Date of Publication if any updated/revised publication

    cover	String	
Path Location of Publication cover

    pdf	String	
Path Location of Publication File

    size	String	
Size File of Publication



### Success Response
```http
    HTTP/1.1 200 OK
    {
    "status": "OK",
    "data-availability": "available",
    "data": [
        {
            "page": 0,
            "pages": 1,
            "per_page": 10,
            "count": 3,
            "total": 3
      },
       [
           {
               "pub_id": "2016320000032000321313",
                "title": "Indeks Pembangunan Manusia Provinsi Jawa Barat 2015",
                "issn": "999-999-999-9",
                "sch_date": "2016-11-28",
                "rl_date": "2016-11-29",
             "updt_date": null,
              "cover": "http://publikasi.bps.go.id/portalpublikasi_beta/index.php/publikasi/getcover?id=2016320000032000321313",
              "pdf": "http://publikasi.bps.go.id/portalpublikasi_beta/index.php/publikasi/getpdfwatermark?id=2016320000032000321313",
                "size": "5 MB"
            },
            {
                "pub_id": "20163200000320003211",
                "title": "Provinsi Jawa Barat Dalam Angka 2016",
                "issn": "0215-2169",
                "sch_date": "2016-11-16",
                "rl_date": "2016-11-16",
                "updt_date": "2016-11-23",
                "cover": "http://publikasi.bps.go.id/portalpublikasi_beta/index.php/publikasi/getcover?id=20163200000320003211",
                "pdf": "http://publikasi.bps.go.id/portalpublikasi_beta/index.php/publikasi/getpdfwatermark?id=20163200000320003211",
               "size": "2.8 MB"
            },
           {
              "pub_id": "2016320000032000322302",
             "title": "[Updated] Testing Publikasi NON-ARC",
            "issn": "-",
           "sch_date": null,
          "rl_date": "2016-11-15",
        "updt_date": "2017-01-27",
                "cover": "http://publikasi.bps.go.id/portalpublikasi_beta/index.php/publikasi/getcover?id=2016320000032000322302",
                "pdf": "http://www.bps.go.id",
                "size": "30 MB"
            }
        ]
    ]
}
```


### Error 4xx
Name	Description
UserNotFound	
The id of the User was not found.



### Error Response
```http
HTTP/1.1 404 Not Found
  {
    "error": "UserNotFound"
  }
```

Strategic Indicators
List Strategic Indicators
This service is used to displays all strategic indicator only for the central and province website


**Endpoint:** `https://webapi.bps.go.id/v1/api/list/`


### Parameter
Field	Type	Description
model	String	
Model to display strategic indicators for strategic indicators is "indicators"

lang optional	String	
Language to display strategic indicators

Default value: ind

Allowed values: "ind", "eng"

domain	Number	
Domains that will be displayed derived period data (see master domain). Domains that allowed in this model only for central and province domain.

Size range: 4

var optional	Number	
Variable ID selected to display derived period data

Allowed values: 1, 2, 3, 4, ..., n

page optional	Number	
Page to display derived period data

Allowed values: 1, 2, 3, 4, ..., n

key	String	
Key app to access API


### Send a Sample Request



### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status of list indicators.

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  1	Object	
List Strategic Indicators

    title	String	
Title of Strategic Indicators

    desc	String	
Description of Indicators

    data_source	String	
Data Source if Strategic Indicators

    value	Number	
Value of Strategic Indicators

    unit	String	
Unit Value of Strategic Indicators



### Success Response
```http
HTTP/1.1 200 OK
      {
        "status": "OK",
        "data-availability": "available",
        "data":[{
        "page":1,
        "pages":230,
        "per_page":10,
        "count":10,
        "total":2300
      },
      [{
      "turth_id":0,
      "turth":"Tahun",
      "group_turth_id":0,
      "name_group_turth":"Tahunan"
    },{
    "turth_id":1,
    "turth":"Bulanan",
    "group_turth_id":1,
    "name_group_turth":"January"
  },{
  "turth_id":2,
  "turth":"Bulanan",
  "group_turth_id":2,
  "name_group_turth":"February"
}]
]

}
```


### Error 4xx
Name	Description
UserNotFound	
The id of the User was not found.



### Error Response
```http
HTTP/1.1 404 Not Found
  {
    "error": "UserNotFound"
  }
```


## Infographic
List All Infographic
This service is used to displays all infographic in the website


**Endpoint:** `https://webapi.bps.go.id/v1/api/list/`


### Parameter
Field	Type	Description
model	String	
Model to display news (news) for infographic is "infographic"

lang optional	String	
Language to display news

Default value: ind

Allowed values: "ind", "eng"

domain	Number	
Domains that will be displayed news (see master domain)

Size range: 4

page optional	Number	
Page to display news

Allowed values: 1, 2, 3, 4, ..., n

keyword optional	String	
Keyword to search

key	String	
Key app to access API


### Send a Sample Request



### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status of list indicators.

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  1	Object	
List Infographics

    inf_id	Number	
Id of Infographic

    title	String	
Title of Infographic

    img	String	
Thumbnail of Infographic

    desc	String	
Description of infographic

    category	Number	
Category id of infographic (1: Social and Population, 2: Economic and Trade, 3: Agriculture and Mining)

    dl	String	
Download link of Infographic



### Success Response
```http
HTTP/1.1 200 OK
{
  "status": "OK",
  "data-availability": "available",
  "data": [
    {
      "page": 1,
      "pages": 49,
      "per_page": 10,
      "count": 10,
      "total": 481
    },
      [
        {
          "inf_id": 527,
          "title": "Transportasi Rilis Oktober 2020",
          "img": "https://www.bps.go.id/website/images/Transportasi-Rilis-Oktober-2020-ind.jpg",
          "desc": "",
          "category": 2,
          "dl": "https://www.bps.go.id/galery/download.html?asdf=NTI3&qwer=ldjfdifsdjkfahi&zxcv=MjAyMC0xMC0wNiAwNzozMzowMg%3D%3D"
        },
      ]
    ] 

}
```


### Error 4xx
Name	Description
UserNotFound	
The id of the User was not found.



### Error Response
```http
HTTP/1.1 404 Not Found
  {
    "error": "UserNotFound"
  }
```


## Glosarium
List of Glosarium
This service is used to display list of glosarium


**Endpoint:** `https://webapi.bps.go.id/v1/api/list`


### Parameter
Field	Type	Description
model	String	
Model to display list of glosarium is "glosarium"

prefix optional	String	
The first letter that the list will look for

page optional	Number	
Page to display subject

Allowed values: 1, 2, 3, 4, ..., n

perpage optional	Number	
Sum of Table to display per page

Allowed values: 1, 2, 3, 4, ..., 500

key	String	
Key app to access API


### Send a Sample Request



### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  _source	Object	
Data List

    konten	String	
Content: Glosarium

    jenis	String	
Type of content: Glosarium

    id	Number	
Unique ID of glosarium

    idSds	Number	
Unique ID of SDS

    noIndikator	Number	
Number of Indicator

    judulIndikator	String	
Title of Indicator in Bahasa

    judulIndikator_en	String	
Title of Indicator in English

    konsep	String	
Statistical Concept in Bahasa

    konsep_en	String	
Statistical Concept in English

    definisi	String	
Definition of a Statistical Concept in Bahasa

    definisi_en	String	
Definition of a Statistical Concept in English

    namaKlasifikasi	String	
Name of Classification in Bahasa

    namaKlasifikasi_en	String	
Name of Classification in English

    ukuran	String	
Size in Bahasa

    ukuran_en	String	
Size in English

    satuan	String	
unit in Bahasa

    satuan_en	String	
unit in English

    flagSds	String	
Flag of Sds

    sumberKonten	String	
Source of content in Bahasa

    sumberKonten_en	String	
Source of Content in English

    sumberData	String	
Source of Data in Bahasa

    sumberData_en	String	
Source of data in English

    Endpoint	String	
Type of ENdpoint

    flag	boolean	


### Success Response
```http
HTTP/1.1 200 OK
{
  "status": "OK",
  "data-availability": "available",
  "data": [
    {
      "page": 1,
      "pages": 508,
      "per_page": 10,
      "count": 10,
      "total": 5078
    },
    [
      {
        "_index": "glosarium",
        "_type": "_doc",
        "_id": "glosarium_4406_web",
        "_score": null,
        "_source": {
          "konten": "glosarium",
          "jenis": "glosarium",
          "id": "4406",
          "idSds": null,
          "noIndikator": null,
          "judulIndikator": "",
          "judulIndikator_en": "",
          "konsep": "Agama",
          "konsep_en": "Religion",
          "definisi": "Agama merupakan keyakinan terhadap Tuhan Yang Maha Esa yang harus dimiliki oleh setiap manusia. Agama dibedakan menjadi Islam, Kristen, Katholik, Hindu, Budha, Khong Hu Chu, dan Agama Lainnya. Agama berguna dalam menentukan kebijakan yang berkaitan dengan kerukunan umat beragama, contoh: kebijakan Kementerian Agama dalam pembangunan tempat-tempat ibadahberagama, untuk memelihara dan menyuburkan kesadaran umat dalam menghayati danmelaksanakan ajaran-ajarannya. Termasuk dalam acara agama: Sepercik Iman Pembasuh Kalbu,Terjemahan Al-Quran, Mimbar Agama Islam, Mimbar Agama Katolik, Mimbar Agama Protestan.",
          "definisi_en": "Religion is belief in Almighty God that must be possessed by every human being. Religion can be divided into Muslim, Christian, Catholic, Hindu, Buddhist, Hu Khong Chu, and Other Religion. ",
          "namaKlasifikasi": "",
          "namaKlasifikasi_en": "",
          "klasifikasi": "",
          "klasifikasi_en": "",
          "ukuran": "",
          "ukuran_en": "",
          "satuan": "",
          "satuan_en": "",
          "flagSds": "",
          "sumberKonten": "",
          "sumberKonten_en": "",
          "sumberData": "",
          "sumberData_en": "",
          "endpoint": "web",
          "flag": "t"
        },
        "sort": [
          "agama"
        ]
      },
    ]
  ]
}
```


### Error 4xx
Name	Description
UserNotFound	
The id of the User was not found.



### Error Response
```http
HTTP/1.1 404 Not Found
  {
    "error": "UserNotFound"
  }
```

Detail of Glosarium
This service is used to display the detail of statistical concept


**Endpoint:** `https://webapi.bps.go.id/v1/api/view`


### Parameter
Field	Type	Description
model	String	
Model to display list of glosarium is "glosarium"

id	Number	
The ID of glosarium

lang	String	
Language to display

Default value: ind

Allowed values: "ind", "eng"

key	String	
Key app to access API


### Send a Sample Request



### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  _source	Object	
Data List

    konten	String	
Content: Glosarium

    jenis	String	
Type of content: Glosarium

    id	Number	
Unique ID of glosarium

    idSds	Number	
Unique ID of SDS

    noIndikator	Number	
Number of Indicator

    judulIndikator	String	
Title of Indicator in Bahasa

    judulIndikator_en	String	
Title of Indicator in English

    konsep	String	
Statistical Concept in Bahasa

    konsep_en	String	
Statistical Concept in English

    definisi	String	
Definition of a Statistical Concept in Bahasa

    definisi_en	String	
Definition of a Statistical Concept in English

    namaKlasifikasi	String	
Name of Classification in Bahasa

    namaKlasifikasi_en	String	
Name of Classification in English

    ukuran	String	
Size in Bahasa

    ukuran_en	String	
Size in English

    satuan	String	
unit in Bahasa

    satuan_en	String	
unit in English

    flagSds	String	
Flag of Sds

    sumberKonten	String	
Source of content in Bahasa

    sumberKonten_en	String	
Source of Content in English

    sumberData	String	
Source of Data in Bahasa

    sumberData_en	String	
Source of data in English

    Endpoint	String	
Type of ENdpoint

    flag	boolean	


### Success Response
```http
HTTP/1.1 200 OK
{
  "status": "OK",
  "data-availability": "available",
  "data": [
    {
      "page": 1,
      "pages": 1,
      "per_page": 1,
      "count": 1,
      "total": 1 
    },
    [
      {
        "_index": "glosarium",
        "_type": "_doc",
        "_id": "glosarium_4406_web",
        "_score": null,
        "_source": {
          "konten": "glosarium",
          "jenis": "glosarium",
          "id": "4406",
          "idSds": null,
          "noIndikator": null,
          "judulIndikator": "",
          "judulIndikator_en": "",
          "konsep": "Agama",
          "konsep_en": "Religion",
          "definisi": "Agama merupakan keyakinan terhadap Tuhan Yang Maha Esa yang harus dimiliki oleh setiap manusia. Agama dibedakan menjadi Islam, Kristen, Katholik, Hindu, Budha, Khong Hu Chu, dan Agama Lainnya. Agama berguna dalam menentukan kebijakan yang berkaitan dengan kerukunan umat beragama, contoh: kebijakan Kementerian Agama dalam pembangunan tempat-tempat ibadahberagama, untuk memelihara dan menyuburkan kesadaran umat dalam menghayati danmelaksanakan ajaran-ajarannya. Termasuk dalam acara agama: Sepercik Iman Pembasuh Kalbu,Terjemahan Al-Quran, Mimbar Agama Islam, Mimbar Agama Katolik, Mimbar Agama Protestan.",
          "definisi_en": "Religion is belief in Almighty God that must be possessed by every human being. Religion can be divided into Muslim, Christian, Catholic, Hindu, Buddhist, Hu Khong Chu, and Other Religion. ",
          "namaKlasifikasi": "",
          "namaKlasifikasi_en": "",
          "klasifikasi": "",
          "klasifikasi_en": "",
          "ukuran": "",
          "ukuran_en": "",
          "satuan": "",
          "satuan_en": "",
          "flagSds": "",
          "sumberKonten": "",
          "sumberKonten_en": "",
          "sumberData": "",
          "sumberData_en": "",
          "endpoint": "web",
          "flag": "t"
        },
        "sort": [
          "agama"
        ]
      },
    ]
  ]
}
```


### Error 4xx
Name	Description
UserNotFound	
The id of the User was not found.



### Error Response
```http
HTTP/1.1 404 Not Found
  {
    "error": "UserNotFound"
  }
```

Foreign Trade Data (Export&Import)
This service is used to displays data of foreign trade from the website


**Endpoint:** `https://webapi.bps.go.id/v1/api/dataexim/`


### Parameter
Field	Type	Description
sumber	Number	
Source of the data

1: Export

2: Import

periode	Number	
Period of the data

1: monthly

2: annually

kodehs	number	
HS Code of the data, use separator ; for multiple HS Code. e.g. firstHScode;secondHScode.

jenishs	Number	
Type of HS Code

1: Two digit

2: Full HS Code

If jenishs = 1 then the kodehs is two digits. If jenishs = 2 then the full digit kodehs follows the master hscode by year. For more information

Tahun	String	
Year of data

key	String	
Key app to access API


### Send a Sample Request



### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status of list indicators.

Metadata	Object[]	
source: source of the data

value: Export/Import value in US Dollar ($)

netweight: weight of Export/Import in Kilogram (Kg)

kodehs: Code and Description from HS

pod: Incoming/Outgoing Ports in Indonesia

ctr: Country of Origin/Destination

year: data year



### Success Response
```http
HTTP/1.1 200 OK
{
  "status": "OK",
  "data-availability": "not-available",
  "metadata": {
    "source": "Sumber : https://www.bps.go.id diakses pada 23-06-2021 12:38:14 WIB",
    "value": "Nilai Ekspor/Impor dalam US Dollar ($)",
    "netweight": "Berat Ekspor/Impor dalam Kilogram (KG)",
    "kodehs": "Kode dan Deskripsi dari HS",
    "pod": "Pelabuhan Masuk/Keluar di Indonesia",
    "ctr": "Negara Asal/Tujuan",
    "tahun": "Tahun Data"
  },
  "data": [
    {
      "value": 1015060.142,
      "netweight": 243755,
      "kodehs": "[03] Ikan dan krustasea, moluska serta invertebrata air lainnya",
      "pod": "BELAWAN",
      "ctr": "ALBANIA",
      "tahun": "2019"
    },...

}
```


### Error 4xx
Name	Description
UserNotFound	
The id of the User was not found.



### Error Response
```http
HTTP/1.1 404 Not Found
  {
    "error": "UserNotFound"
  }
```

Sustainable Development Goals (SDGs)
List All SDGs Table
This service is used to displays all SDGs table, domain must be "0000"


**Endpoint:** `https://webapi.bps.go.id/v1/api/list/`


### Parameter
Field	Type	Description
model	String	
Model to display sdgs table is "sdgs"

goal optional	String	
Number of Goal

Allowed values: 1... 17

key	String	
Key app to access API


### Send a Sample Request


SDGs Table List
This table is updated annually without prior notice

Goals	Variable	Variable (id)	Id Var
	Number of Deaths, Disappeared, and Hurt Victims Affected	Jumlah Korban Meninggal, Hilang, dan Terluka Terkena Dampak Bencana	1804
Number of Deaths, Disappeared, and Hurt Victims Affected by 100,000 People	Jumlah Korban Meninggal, Hilang, dan Terluka Terkena Dampak Bencana Per 100.000 Orang	1246
Percentage of Poor People by Province	Persentase Penduduk Miskin Menurut Provinsi	192
Percentage of Poor People by Region	Persentase Penduduk Miskin Menurut Wilayah	184
Percentage of Poor People In Disadvantaged Areas	Persentase Penduduk Miskin Di Daerah Tertinggal	1238
Percentage of population living below the national poverty line, according to age group	Persentase Penduduk Yang Hidup Di Bawah Garis Kemiskinan Nasional, Menurut Kelompok Umur	1539
Percentage of Population Living Below the National Poverty Line, According to Gender	Persentase Penduduk Yang Hidup di Bawah Garis Kemiskinan Nasional, Menurut Jenis Kelamin	1538
Proportion of households with access to basic services by area of residence	Proporsi rumah tangga dengan akses terhadap pelayanan dasar menurut Daerah Tempat Tinggal	2017
Proportion of households with access to basic services by province	Proporsi rumah tangga dengan akses terhadap pelayanan dasar menurut provinsi	2016
Proportion of households with ownership and lease / contract status by province	Proporsi rumah tangga dengan status kepemilikan rumah milik dan sewa/kontrak menurut provinsi	2018
Proportion of households with ownership status of owned and leased / contracted houses according to gender	Proporsi rumah tangga dengan status kepemilikan rumah milik dan sewa/kontrak menurut jenis kelamin	2020
Proportion of households with ownership status of owned and leased / contracted houses by area of residence	Proporsi rumah tangga dengan status kepemilikan rumah milik dan sewa/kontrak menurut Daerah Tempat Tinggal	2019
Spending on basic services (education, health and social protection) as a percentage of total government spending.	Pengeluaran untuk layanan pokok (pendidikan, kesehatan dan perlindungan sosial) sebagai persentase dari total belanja pemerintah	1759

Agricultural Added Value Divided by Number of Labor in Agricultural Sector	Nilai Tambah Pertanian Dibagi Jumlah Tenaga Kerja Di Sektor Pertanian	1344
Percentage of Toddlers (Under Five Years Old) Short And Very Short	Persentase Balita Pendek Dan Sangat Pendek	1325
Population Prevalence With Moderate Or Severe Food Insecurity, Based On The Scale Of Food Insecurity Experience	Prevalensi Penduduk Dengan Kerawanan Pangan Sedang Atau Berat, Berdasarkan Pada Skala Pengalaman Kerawanan Pangan	1474
Prevalence of Anemia in Pregnant Women	Prevalensi Anemia Pada Ibu Hamil	1333
Prevalence of Insufficient Food Consumption	Prevalensi Ketidakcukupan Konsumsi Pangan	1473
Prevalence of Toddler Very Short and Short in Regency / City SSGBI	Prevalensi Balita Sangat Pendek dan Pendek pada Kabupaten/Kota SSGBI	1614
The prevalence of anemia in pregnant women according to age group	Prevalensi anemia pada ibu hamil menurut kelompok umur	1782
Toddler Prevalence is Very Short and Short by Regency / City in 2018	Prevalensi Balita Sangat Pendek dan Pendek Menurut Kabupaten/Kota Tahun 2018	1531

Age Specific Fertility Rate/ASFR (15-19) by Area	Angka Kelahiran Pada Perempuan Usia 15-19 Tahun Menurut Daerah Tempat Tinggal	1398
Age Specific Fertility Rate/ASFR (15-19) by Province	Angka Kelahiran Pada Perempuan Usia 15-19 Tahun Menurut Provinsi	1397
Alcohol consumption by people aged ≥ 15 years in the past year	Konsumsi Alkohol Oleh Penduduk Umur ≥ 15 Tahun Dalam Satu Tahun Terakhir	1475
Birth Rate In Women Aged 15-19 Years by Provinsi	Angka Kelahiran Pada Perempuan Umur 15-19 Tahun Menurut Provinsi	1353
Birth Rates for Women Aged 15-19 Years by Region of Residence	Angka Kelahiran Pada Perempuan Umur 15-19 Tahun (ASFR) (per 1.000 perempuan umur 15-19 tahun) Menurut Daerah Tempat Tinggal	1612
Density and Distribution of Health Workers	Kepadatan Dan Distribusi Tenaga Kesehatan	1477
Incidence of Tuberculosis (ITB) Per 100,000 Population	Insiden Tuberkolosis (ITB) Per 100.000 Penduduk	1763
Infant Mortality Rate (IMR) Per 1000 Live Births According to Wealth Quantile	Angka Kematian Bayi (AKB) Per 1000 Kelahiran Hidup Menurut Kuantil Kekayaan	1572
Infant Mortality Rate (IMR) Per 1000 Live Births by Age of Mother During Childbirth	Angka Kematian Bayi (AKB) Per 1000 Kelahiran Hidup Menurut Umur Ibu Saat Melahirkan	1569
Infant Mortality Rate (IMR) Per 1000 Live Births by Province	Angka Kematian Bayi (AKB) Per 1000 Kelahiran Hidup Menurut Provinsi	1584
Infant Mortality Rate (IMR) Per 1000 Live Births by Residence Area	Angka Kematian Bayi (AKB) Per 1000 Kelahiran Hidup Menurut Daerah Tempat Tinggal	1568
Infant Mortality Rate (IMR) Per 1000 Live Births of Mothers Education	Angka Kematian Bayi (AKB) Per 1000 Kelahiran Hidup Menurut Pendidikan Ibu	1574
Malaria Occurrences Per 1000 Persons	Kejadian Malaria Per 1000 Orang	1393
Maternal Mortality Rate by Island	Angka Kematian Ibu Menurut Pulau	1349
Mortality Rate Per 1000 Live Births by Area of Residence	Angka Kematian Balita Per 1000 Kelahiran Hidup Menurut Daerah Tempat Tinggal	1379
Mortality Rate Per 1000 Live Births by Maternal age at delivery	Angka Kematian Balita Per 1000 Kelahiran Hidup Menurut Umur Ibu saat Melahirkan	1381
Mortality Rate Per 1000 Live Births by Mother education level	Angka Kematian Balita Per 1000 Kelahiran Hidup Menurut Pendidikan Ibu	1374
Mortality Rate Per 1000 Live Births by Province	Angka Kematian Balita Per 1000 Kelahiran Hidup Menurut Provinsi	1373
Mortality Rate Per 1000 Live Births by Wealth Quintile	Angka Kematian Balita Per 1000 Kelahiran Hidup Menurut Kuantil Kekayaan	1382
Neonatal Death Rate And Infant Mortality Rate Per 1000 Birth By Area Of Residence	Angka Kematian Neonatal (AKN) Dan Angka Kematian Bayi Per 1000 Kelahiran Menurut Daerah tempat tinggal	1384
Neonatal Death Rate And Infant Mortality Rate Per 1000 Birth By Maternal age at delivery	Angka Kematian Neonatal (AKN) Dan Angka Kematian Bayi Per 1000 Kelahiran Menurut Umur Ibu saat Melahirkan	1388
Neonatal Death Rate And Infant Mortality Rate Per 1000 Birth By Mother education level	Angka Kematian Neonatal (AKN) Dan Angka Kematian Bayi Per 1000 Kelahiran Menurut Pendidikan Ibu	1385
Neonatal Death Rate And Infant Mortality Rate Per 1000 Birth By Province	Angka Kematian Neonatal (AKN) Dan Angka Kematian Bayi Per 1000 Kelahiran Menurut Provinsi	1383
Neonatal Death Rate And Infant Mortality Rate Per 1000 Birth By Wealth quintile	Angka Kematian Neonatal (AKN) Dan Angka Kematian Bayi Per 1000 Kelahiran Menurut Kuantil Kekayaan	1387
Number of Clients Accessing Post-rehabilitation Services	Jumlah Klien Yang Mengakses Layanan Pascarehabilitasi	1479
Number of districts / cities that have achieved malaria elimination	Jumlah Kabupaten/Kota yang mencapai eliminasi Malaria	1764
Number of districts / cities with filariasis elimination (successfully passed the phase I transmission assessment survey)	Jumlah Kabupaten/Kota dengan eliminasi filariasis (berhasil lolos dalam survei penilaian transmisi tahap I)	1778
Number of People Accessing Post Rehabilitation Services	Jumlah yang Mengakses Layanan Pasca Rehabilitasi	1790
Number of Population Which Is Included Health Insurance Or Public Health System Per 1000 people	Jumlah Penduduk Yang Dicakup Asuransi Kesehatan Atau Sistem Kesehatan Masyarakat per 1000 Penduduk	1434
Number of Provinces with Leprosy Elimination	Jumlah Provinsi dengan eliminasi Kusta	1770
Percentage of Smokers Age √¢‚Ä∞¬• 15 years by Age	Persentase Merokok Pada Penduduk Umur ≥ 15 Tahun Menurut Kelompok Umur	1438
Percentage of Smokers Age √¢‚Ä∞¬• 15 years by Area	Persentase Merokok Pada Penduduk Umur ≥ 15 Tahun Menurut Daerah Tempat Tinggal	1436
Percentage of Smokers Age √¢‚Ä∞¬• 15 years by Percentile Group of Expenditure	Persentase Merokok Pada Penduduk Umur ≥ 15 Tahun Menurut Kelompok Pengeluaran	1437
Percentage of Smokers Age √¢‚Ä∞¬• 15 years by Province	Persentase Merokok Pada Penduduk Umur ≥ 15 Tahun Menurut Provinsi	1435
Persentase Perempuan Pernah Kawin Berusia 15-49 Tahun Yang Proses Kelahiran Terakhirnya Ditolong Oleh Tenaga Kesehatan Terlatih Menurut Daerah Tempat Tinggal	Persentase Perempuan Pernah Kawin Berusia 15-49 Tahun Yang Proses Kelahiran Terakhirnya Ditolong Oleh Tenaga Kesehatan Terlatih Menurut Daerah Tempat Tinggal	1346
Persentase Perempuan Pernah Kawin Berusia 15-49 Tahun Yang Proses Kelahiran Terakhirnya Ditolong Oleh Tenaga Kesehatan Terlatih Menurut Kelompok Pengeluaran	Persentase Perempuan Pernah Kawin Berusia 15-49 Tahun Yang Proses Kelahiran Terakhirnya Ditolong Oleh Tenaga Kesehatan Terlatih Menurut Kelompok Pengeluaran	1347
Persentase Perempuan Pernah Kawin Berusia 15-49 Tahun Yang Proses Kelahiran Terakhirnya Ditolong Oleh Tenaga Kesehatan Terlatih Menurut Provinsi	Persentase Perempuan Pernah Kawin Berusia 15-49 Tahun Yang Proses Kelahiran Terakhirnya Ditolong Oleh Tenaga Kesehatan Terlatih Menurut Provinsi	1345
Prevalence of high blood pressure according to sex	Prevalensi tekanan darah tinggi menurut jenis kelamin	1780
Prevalence of high blood pressure according to the area of residence	Prevalensi tekanan darah tinggi menurut daerah tempat tinggal	1779
Prevalence of High Blood Pressure by Province	Prevalensi Tekanan Darah Tinggi Menurut Provinsi	1480
Prevalence of Obesity in Age Population> 18 Years Old	Prevalensi Obesitas Pada Penduduk Umur > 18 Tahun	1481
The Number Of Drug Abuse And Harmful Alcohol Users, Who Access Medical Rehabilitation Services	Jumlah Penyalahgunaan Narkotika dan Pengguna Alkohol Yang Merugikan, Yang Mengakses Layanan Rehabilitasi Medis	1789
The prevalence of obesity in people aged> 18 years according to sex	Prevalensi Obesitas Pada Penduduk Umur > 18 Tahun Menurut Jenis Kelamin	1781
The proportion of women of reproductive age (15-49 years) or their partners who have family planning needs and use contraception methods	Proporsi Perempuan Usia Reproduksi (15-49 tahun) atau Pasangannya yang Memiliki Kebutuhan Keluarga Berencana dan Menggunakan Alat Kontrasepsi Metode Modern	1394
Total Fertility Rate by Area	Angka Kelahiran Total Menurut Daerah Tempat Tinggal	1401
Total Fertility Rate by Expenditure Groups	Angka Kelahiran Total Menurut Kelompok Pengeluaran	1400
Total Fertility Rate by Province	Angka Kelahiran Total Menurut Provinsi	1399
Unmet Need Pelayanan Kesehatan Menurut Daerah Tempat Tinggal	Unmet Need Pelayanan Kesehatan Menurut Daerah Tempat Tinggal	1403
Unmet Need Pelayanan Kesehatan Menurut Jenis Kelamin	Unmet Need Pelayanan Kesehatan Menurut Jenis Kelamin	1404
Unmet Need Pelayanan Kesehatan Menurut Kelompok Pengeluaran	Unmet Need Pelayanan Kesehatan Menurut Kelompok Pengeluaran	1405
Unmet Need Pelayanan Kesehatan Menurut Kelompok Umur	Unmet Need Pelayanan Kesehatan Menurut Kelompok Umur	1406
Unmet Need Pelayanan Kesehatan Menurut Provinsi	Unmet Need Pelayanan Kesehatan Menurut Provinsi	1402

Education Completion Rate According to Education Level and Expenditure Group	Tingkat Penyelesaian Pendidikan Menurut Jenjang Pendidikan dan Kelompok Pengeluaran	1983
Education Completion Rate According to Education Level and Gender	Tingkat Penyelesaian Pendidikan Menurut Jenjang Pendidikan dan Jenis Kelamin	1982
Education Completion Rate According to Education Level and Province	Tingkat Penyelesaian Pendidikan Menurut Jenjang Pendidikan dan Provinsi	1980
Education Completion Rate According to Education Level and Region	Tingkat Penyelesaian Pendidikan Menurut Jenjang Pendidikan dan Wilayah	1981
Literacy Rate (AMH) of Population above 15 Years Old by Area	Angka Melek Huruf Penduduk Berumur 15 Tahun Ke Atas Menurut Daerah Tempat Tinggal	1461
Literacy Rate (AMH) of Population above 15 Years Old by Group of Income	Angka Melek Huruf Penduduk Berumur 15 Tahun Ke Atas Menurut Kelompok Pendapatan	1459
Literacy Rate (AMH) of Population above 15 Years Old by Province	Angka Melek Huruf Penduduk Berumur 15 Tahun Ke Atas Menurut Provinsi	1458
Literacy Rate (AMH) of Population above 15 Years Old by Sex	Angka Melek Huruf Penduduk Berumur 15 Tahun Ke Atas Menurut Jenis Kelamin	1460
Number of Children Out of School by Education Level and Area of Residence	Angka Anak Tidak Sekolah Menurut Jenjang Pendidikan dan Daerah Tempat Tinggal	1984
Number of Children Out of School by Education Level and Expenditure Group	Angka Anak Tidak Sekolah Menurut Jenjang Pendidikan dan Kelompok Pengeluaran	1988
Number of Children Out of School by Education Level and Gender	Angka Anak Tidak Sekolah Menurut Jenjang Pendidikan dan Jenis Kelamin	1986
Participation rate in organized learning (one year before primary school age) by Gender	Tingkat partisipasi dalam pembelajaran yang teroganisir (satu tahun sebelum usia sekolah dasar) menurut Jenis Kelamin	1994
Participation rate in organized learning (one year before primary school age) by province	Tingkat partisipasi dalam pembelajaran yang teroganisir (satu tahun sebelum usia sekolah dasar) menurut provinsi	1990
Participation rate in organized learning (one year before primary school age) by Residence	Tingkat partisipasi dalam pembelajaran yang teroganisir (satu tahun sebelum usia sekolah dasar) menurut Daerah Tempat Tinggal	1992
Proportion of Adolescents And Adults Aged 15-24 Years With The Information and Computer Technology Skills (ICT) by Area	Proporsi Remaja Dan Dewasa Usia 15-24 Tahun Dengan Keterampilan Teknologi Informasi Dan Komputer (TIK) Menurut Daerah Tempat Tinggal	1453
Proportion of Adolescents And Adults Aged 15-24 Years With The Information and Computer Technology Skills (ICT) by Province	Proporsi Remaja Dan Dewasa Usia 15-24 Tahun Dengan Keterampilan Teknologi Informasi Dan Komputer (TIK) Menurut Provinsi	1451
Proportion of Adolescents And Adults Aged 15-24 Years With The Information and Computer Technology Skills (ICT) by Sex	Proporsi Remaja Dan Dewasa Usia 15-24 Tahun Dengan Keterampilan Teknologi Informasi Dan Komputer (TIK) Menurut Jenis Kelamin	1454
Proportion of Adolescents And Adults Aged 15-59 Years With The Information and Computer Technology Skills (ICT) by Area	Proporsi Remaja Dan Dewasa Usia 15-59 Tahun Dengan Keterampilan Teknologi Informasi Dan Komputer (TIK) Menurut Daerah Tempat Tinggal	1449
Proportion of Adolescents And Adults Aged 15-59 Years With The Information and Computer Technology Skills (ICT) by Province	Proporsi Remaja Dan Dewasa Usia 15-59 Tahun Dengan Keterampilan Teknologi Informasi Dan Komputer (TIK) Menurut Provinsi	1447
Proportion of Adolescents And Adults Aged 15-59 Years With The Information and Computer Technology Skills (ICT) by Sex	Proporsi Remaja Dan Dewasa Usia 15-59 Tahun Dengan Keterampilan Teknologi Informasi Dan Komputer (TIK) Menurut Jenis Kelamin	1450
Proportion of Schools with Access to Proper Water Source Facilities	Proporsi Sekolah dengan Akses Fasilitas Sumber Air Layak	1797
Proportion of Schools with Computer Access	Proporsi Sekolah dengan Akses Komputer	1796
Proportion of Schools with Electricity Access	Proporsi Sekolah dengan Akses Listrik	1794
Ratio of Pure Participation Participation (APM) Female / Male by Area	Rasio Angka Partisipasi Murni (APM) Perempuan/Laki-Laki Menurut Daerah Tempat Tinggal	1456
Ratio of Pure Participation Participation (APM) Female / Male by Province	Rasio Angka Partisipasi Murni (APM) Perempuan/Laki-Laki Menurut Provinsi	1455
Ratio of Pure Participation Participation (APM) Female / Male by Revenue Group (Expenditures)	Rasio Angka Partisipasi Murni (APM) Perempuan/Laki-Laki Menurut Kelompok Pendapatan (Pengeluaran)	1608
Ratio of Pure Participation Rate (APM) for Women / Men by Expenditure Group	Rasio Angka Partisipasi Murni (APM) Perempuan/Laki-Laki Menurut Kelompok Pendapatan	1607
Rough Participation Rate of University by Area	Angka Partisipasi Kasar (APK) Perguruan Tinggi (PT) Menurut Daerah Tempat Tinggal	1445
Rough Participation Rate of University by Groups of Expenditure	Angka Partisipasi Kasar (APK) Perguruan Tinggi (PT) Menurut Kelompok Pengeluaran	1444
Rough Participation Rate of University by Province	Angka Partisipasi Kasar (APK) Perguruan Tinggi (PT) Menurut Provinsi	1443
Rough Participation Rate of University by Sex	Angka Partisipasi Kasar (APK) Perguruan Tinggi (PT) Menurut Jenis Kelamin	1446
Youth and adult participation rates in formal and non-formal education and training in the last 12 months, by gender	Tingkat partisipasi remaja dan dewasa dalam pendidikan dan pelatihan formal dan non formal dalam 12 bulan terakhir, menurut jenis kelamin	1998
Youth and adult participation rates in formal and non-formal education and training in the last 12 months, by Residence	Tingkat partisipasi remaja dan dewasa dalam pendidikan dan pelatihan formal dan non formal dalam 12 bulan terakhir, menurut Daerah Tempat Tinggal	1996
Youth and adult participation rates in formal and non-formal education and training in the past 12 months, according to Expenditure Groups	Tingkat partisipasi remaja dan dewasa dalam pendidikan dan pelatihan formal dan non formal dalam 12 bulan terakhir, menurut Kelompok Pengeluaran	2000

Level of Proportion of women in managerial positions, according to marital status	Proporsi perempuan yang berada di posisi managerial, menurut status perkawinan	2007
Level of Proportion of women in managerial positions, by area of residence	Proporsi perempuan yang berada di posisi managerial, menurut Daerah Tempat Tinggal	2004
Level Proportion of women in managerial positions by province	Proporsi perempuan yang berada di posisi managerial menurut provinsi	2003
Level The proportion of women in managerial positions, by education level	Proporsi perempuan yang berada di posisi managerial, menurut tingkat pendidikan	2006
Percentage of Seats Occupied In DPR and DPRD	Persentase Kursi Yang Diduduki Perempuan Di DPR Dan DPRD	1337
Proportion of Adult Women and Girls (Aged 15-64 Years) Experiencing Violence (Physical, Sexual, Or Emotional) By Couples Or Former Couples In The Last 12 Months	Proporsi Perempuan Dewasa Dan Anak Perempuan (Umur 15-64 Tahun) Mengalami Kekerasan (Fisik, Seksual, Atau Emosional) Oleh Pasangan Atau Mantan Pasangan Dalam 12 Bulan Terakhir	1375
Proportion of Adult Women and Girls (Aged 15-64 Years) Experiencing Violence (Physical, Sexual, Or Emotional) By Couples Or Former Couples In The Last 12 Months by Type of Violence	Proporsi Perempuan Dewasa Dan Anak Perempuan (Umur 15-64 Tahun) Mengalami Kekerasan (Fisik, Seksual, Atau Emosional) Oleh Pasangan Atau Mantan Pasangan Dalam 12 Bulan Terakhir Menurut Jenis Kekerasan	1378
Proportion of Adult Women and Girls (Ages 15-64 Years) Experiencing Sexual Violence By Others In addition to Couples In The Last 12 Months	Proporsi Perempuan Dewasa Dan Anak Perempuan (Umur 15-64 Tahun) Mengalami Kekerasan Seksual Oleh Orang Lain Selain Pasangan Dalam 12 Bulan Terakhir	1362
Proportion of Individuals Using Mobile Phones	Proporsi Individu Yang Menggunakan Telepon Genggam	1221
Proportion of Individuals Who Use Mobile Phones by Age Group	Proporsi Individu Yang Menggunakan Telepon Genggam Menurut Kelompok Umur	1222
Proportion of Individuals Who Use Mobile Phones by Sex	Proporsi Individu Yang Menggunakan Telepon Genggam Menurut Jenis Kelamin	1224
Proportion of Women Aged 20-24 Years Who Are Married Or Living Status Together Before Age 15 Years	Proporsi Perempuan Umur 20-24 Tahun Yang Berstatus Kawin Atau Berstatus Hidup Bersama Sebelum Umur 15 Tahun	1358
Proportion of Women Aged 20-24 Years Who Are Married or Living Status Together Before Age 15 Years by Area of Residence	Proporsi Perempuan Umur 20-24 Tahun Yang Berstatus Kawin Atau Berstatus Hidup Bersama Sebelum Umur 15 Tahun Menurut Daerah Tempat Tinggal	1359
Proportion of Women Aged 20-24 Years Who Are Married or Living Status Together Before Age 18 Years By Area of Residence	Proporsi Perempuan Umur 20-24 Tahun Yang Berstatus Kawin Atau Berstatus Hidup Bersama Sebelum Umur 18 Tahun Menurut Daerah Tempat Tinggal	1361
Proportion of Women Aged 20-24 Years Who Are Married Or Living Status Together Before Age 18 Years by Province	Proporsi Perempuan Umur 20-24 Tahun Yang Berstatus Kawin Atau Berstatus Hidup Bersama Sebelum Umur 18 Tahun Menurut Provinsi	1360

Percentage of Household Population by Province and Improved Sanitation	Persentase Rumah Tangga menurut Provinsi dan Memiliki Akses terhadap Sanitasi Layak	847
Percentage of Industrial Wastewater Flows Safely Treated	Persentase Limbah Cair Industri Cair yang Diolah Secara Aman	1279
Proportion of Hazardous and Toxic Waste (B3) Processed In accordance with the Regulations	Proporsi Limbah Bahan Berbahaya dan Beracun (B3) Yang Diolah Sesuai Peraturan	1281
Proportion of Households Having Hand Washing Facility With Soap And Water By Province	Proporsi Rumah Tangga Yang Memiliki Fasilitas Cuci Tangan Dengan Sabun Dan Air Menurut Provinsi	1273
Proportion of Households Who Have Access to Decent Sanitation Service by Area of Residence	Proporsi Rumah Tangga Penduduk Yang Memiliki Akses Terhadap Layanan Sanitasi Layak Dan Berkelanjutan Menurut Daerah Tempat Tinggal	1270
Proportion of Households Who Have Handwashing Facility With Soap And Water by Area of Residence	Proporsi Rumah Tangga Yang Memiliki Fasilitas Cuci Tangan Dengan Sabun Dan Air Menurut Daerah Tempat Tinggal	1274
Proportion of Population Populations Who Have Access to Decent and Sustainable Sanitation Services By Revenue Group	Persentase Rumah Tangga yang Memiliki Akses Terhadap Layanan Sanitasi Layak Menurut Kelompok Pengeluaran	1272

Electricity Consumption per Capita	Konsumsi Listrik per Kapita	1156
Electrification Ratio	Rasio Elektrifikasi	1155
Number of gas network connections for households	Jumlah sambungan jaringan gas untuk rumah tangga	1786
Primary Energy Intensity	Intensitas Energi Primer	1808
Ratio of Domestic Gas Use	Rasio Penggunaan Gas Rumah Tangga	1157
Supply of Primary Energy	Bauran Energi Terbarukan	1824

[2010 Version] Growth Rate of per Capita Gross Regional Domestic Product at 2010 Constant Market Prices	[Seri 2010] Laju Pertumbuhan Produk Domestik Regional Bruto Per Kapita Atas Dasar Harga Konstan 2010	296
[2010 Version] Per Capita Gross Regional Domestic Product by Province	[Seri 2010] Produk Domestik Regional Bruto Per Kapita	288
Average Working Hourly Wage by Province	Upah Rata - Rata Per Jam Pekerja Menurut Provinsi	1172
Average Working Hour Rate by Area of Residence	Upah Rata - Rata Per Jam Pekerja Menurut Daerah Tempat Tinggal	1173
Average Working Hours Period by Age Group	Upah Rata - Rata Per Jam Pekerja Menurut Kelompok Umur	1176
Average Working Hours Rate by Education Level	Upah Rata - Rata Per Jam Pekerja Menurut Tingkat Pendidikan	1175
Average Working Hours Wage by Gender	Upah Rata - Rata Per Jam Pekerja Menurut Jenis Kelamin	1174
Growth Rate of GDP Per Labor / Growth Rate of Real GDP Per Person Work Per Year	Laju Pertumbuhan PDB Per Tenaga Kerja/Tingkat Pertumbuhan PDB Riil Per Orang Bekerja Per Tahun	1161
Half Unemployment Rate by Age Group	Tingkat Setengah Pengangguran Menurut Kelompok Umur	1185
Half Unemployment Rate by Area of Residence	Tingkat Setengah Pengangguran Menurut Daerah Tempat Tinggal	1182
Half Unemployment Rate by Education Level	Tingkat Setengah Pengangguran Menurut Tingkat Pendidikan	1184
Half Unemployment Rate by Province	Tingkat Setengah Pengangguran Menurut Provinsi	1181
Half Unemployment Rate by Sex	Tingkat Setengah Pengangguran Menurut Daerah Jenis Kelamin	1183
Number of foreign tourist visits per month to Indonesia according to the entrance, 2008 - 2017	Jumlah Kunjungan Wisatawan Mancanegara per bulan ke Indonesia Menurut Pintu Masuk, 2008 - 2017	74
Number of foreign tourist visits per month to Indonesia according to the entrance, 2017 - now	Jumlah Kunjungan Wisatawan Mancanegara per bulan ke Indonesia Menurut Pintu Masuk, 2017 - sekarang	1150
Number of Foreign Tourist Visits to Indonesia by Nationality, 2000-2014	Jumlah Kunjungan Wisatawan Mancanegara ke Indonesia Menurut Kebangsaan, 2000-2014	351
Number of Foreign Tourist Visits to Indonesia by Nationality, 2015-now	Jumlah Kunjungan Wisatawan Mancanegara ke Indonesia Menurut Kebangsaan	1821
Number of Nusantara Tourist Travels	Jumlah Perjalanan Wisatawan Nusantara	1189
Percentage and number of working children aged 10-17 years by province	Persentase dan jumlah anak usia 10-17 tahun yang bekerja menurut provinsi	2008
Percentage and number of working children aged 10-17 years by sex	Persentase dan jumlah anak usia 10-17 tahun yang bekerja menurut jenis kelamin	2009
Percentage of Young Age (15-24 Years) Who Are Not School, Working Or Following Training	Persentase Usia Muda (15-24 Tahun) Yang Sedang Tidak Sekolah, Bekerja Atau Mengikuti Pelatihan	1186
Proportion of Informal Employment in Total Employment by Age Group	Proporsi Lapangan Kerja Informal Menurut Kelompok Umur	2156
Proportion of Informal Employment in Total Employment by Educational Level	Proporsi Lapangan Kerja Informal Menurut Tingkat Pendidikan	2157
Proportion of Informal Employment in Total Employment by Province	Proporsi Lapangan Kerja Informal Menurut Provinsi	2153
Proportion of Informal Employment in Total Employment by Sex	Proporsi Lapangan Kerja Informal Menurut Jenis Kelamin	2155
Proportion of Informal Employment in Total Employment by Urban-Rural Classification	Proporsi Lapangan Kerja Informal Menurut Daerah Tempat Tinggal	2154
Proportion of MSME Credits to Total Credit	Proporsi Kredit UMKM Terhadap Total Kredit	1192
Proportion of Tourism Contribution to GDP	Proporsi Kontribusi Pariwisata Terhadap PDB	1188
Total Foreign Exchange of Tourism Sector	Jumlah Devisa Sektor Pariwisata	1160
Unemployment Rate by Age Group	Tingkat Pengangguran Terbuka Berdasarkan Kelompok Umur	1180
Unemployment Rate by Area of Residence	Tingkat Pengangguran Terbuka Berdasarkan Daerah Tempat Tinggal	1178
Unemployment Rate by Education Level	Tingkat Pengangguran Terbuka Berdasarkan Tingkat Pendidikan	1179
Unemployment Rate by Sex	Tingkat Pengangguran Terbuka Berdasarkan Jenis Kelamin	1177

Growth Rate of GDP Manufacturing Industry	Laju Pertumbuhan PDB Industri Manufaktur	1216
Number of Airports In Indonesia By Airport Usage	Jumlah Bandara Di Indonesia Menurut Penggunaan Bandar Udara	1202
Number of Domestic Passengers by Airplane Mode of Transportation by province	Jumlah Penumpang Domestik berdasarkan Moda Transportasi Pesawat Terbang menurut provinsi	2024
Number of Domestic Passengers by Mode of Ship Transportation by province	Jumlah Penumpang Domestik berdasarkan Moda Transportasi Kapal menurut provinsi	2022
Number of Ferry Ports in Indonesia	Jumlah Pelabuhan Penyeberangan Di Indonesia	1208
Number of Ferry Ports in Indonesia by Type of Operation	Jumlah Pelabuhan Penyeberangan Di Indonesia Menurut Jenis Pengoperasian	1210
Number of International Passengers by Airplane Mode of Transportation by province	Jumlah Penumpang Internasional berdasarkan Moda Transportasi Pesawat Terbang menurut provinsi	2027
Number of Passengers based on Railway Transportation Mode	Jumlah Penumpang berdasarkan Moda Transportasi Kereta Api	2051
Number of Strategic Ports	Jumlah Pelabuhan Strategis	1211
Number of Strategic Ports According to Their Management	Jumlah Pelabuhan Strategis Menurut Pengelolaannya	1213
Percentage of Toll Road Lengths Operated By Operator	Persentase Panjang Jalan Tol yang Beroperasi Menurut Operatornya	1200
Proportion of Added Value of Manufacture Sector To GDP	Proporsi Nilai Tambah Sektor Industri Manufaktur Terhadap PDB	1214
Proportion of Added Value of Manufacturing Industry Sector per Capita	Proporsi Nilai Tambah Sektor Industri Manufaktur per Kapita	1215
Proportion of Added Value of Small Industry to Total Value Added Industry	Proporsi Nilai Tambah Industri Kecil Terhadap Total Nilai Tambah Industri	1219
Proportion of Government Research Budget to GDP	Proporsi Anggaran Riset Pemerintah Terhadap PDB	1825
Proportion of Manpower in Manufacturing Industry Sector	Proporsi Tenaga Kerja pada Sektor Industri Manufaktur	1217
Proportion of Small Industry With Loans Or Credit	Proporsi Industri Kecil Dengan Pinjaman Atau Kredit	1220
Railway Network Length In Indonesia	Panjang Jaringan Jalan Rel Kereta Api Di Indonesia	1195
Steady Condition of National Roads	Kondisi Mantap Jalan Nasional	1197

Average Economic Growth In Disadvantaged Areas	Rata-Rata Pertumbuhan Ekonomi Di Daerah Tertinggal	1237
Gini Ratio	Gini Rasio	98
Indonesia Democracy Index (IDI) by Aspect and Province	Indeks Demokrasi Indonesia (IDI) Menurut Aspek dan Provinsi	599
Number of complaints handling of human rights violations of women especially violence against women	Jumlah penanganan pengaduan pelanggaran Hak Asasi Manusia (HAM) perempuan terutama kekerasan terhadap perempuan	1414
Number of Disadvantaged Villages	Jumlah Desa Tertinggal	1231
Number of Independent Villages by Province (Villages)	Jumlah Desa Mandiri Menurut Provinsi	2190
Number of Underdeveloped Villages (Villages)	Jumlah Desa Tertinggal menurut Provinsi (Desa)	2191
Percentage of Budget Plan for Central Government Social Protection Function Expenditures	Persentase Rencana Anggaran Untuk Belanja Fungsi Perlindungan Sosial Pemerintah Pusat	1611
Persentase Penduduk Miskin Menurut Kabupaten/Kota	Persentase Penduduk Miskin Menurut Kabupaten/Kota	621
Proportion of population living below 50 percent of median income, by province	Proporsi penduduk yang hidup di bawah 50 persen dari median pendapatan, menurut provinsi	2011

Number of Deaths, Disappeared, and Hurt Victims Affected	Jumlah Korban Meninggal, Hilang, dan Terluka Terkena Dampak Bencana	1804
Number of Deaths, Disappeared, and Hurt Victims Affected by 100,000 People	Jumlah Korban Meninggal, Hilang, dan Terluka Terkena Dampak Bencana Per 100.000 Orang	1246
Percentage of Households who Have Access To A Decent And Affordable Housing According to the Area of Residence	Persentase Rumah Tangga yang Memiliki Akses Terhadap Hunian Yang Layak Dan Terjangkau Menurut Daerah Tempat Tinggal	1242
Percentage of Households who Have Access To A Decent And Affordable Residential by Province	Persentase Rumah Tangga yang Memiliki Akses Terhadap Hunian Yang Layak Dan Terjangkau Menurut Provinsi	1241
Percentage of households with convenient access (0.5 km distance) to public transportation by province	Persentase rumah tangga yang memiliki akses nyaman (jarak 0.5 km) ke transportasi umum menurut provinsi	2012
Percentage of population aged 10 years and over using public motorized vehicles on certain routes by province	Persentase penduduk berumur 10 tahun ke atas yang menggunakan kendaraan bermotor umum dengan rute tertentu menurut provinsi	2013
Percentage of Victims of Violence in the Last 12 Months Reporting to the Police	Persentase Korban Kekerasan Dalam 12 Bulan Terakhir Yang Melaporkan Kepada Polisi	1252
Percentage of Victims of Violence in the Last 12 Months Reporting to the Police by Sex	Persentase Korban Kekerasan Dalam 12 Bulan Terakhir Yang Melaporkan Kepada Polisi Menurut Jenis Kelamin	1253
Proportion of People Who Became Victims of Violent Violence In The Last 12 Months By Age Group	Proporsi Penduduk Yang Menjadi Korban Kejahatan Kekerasan Dalam 12 Bulan Terakhir Menurut Kelompok Umur	1310
Proportion of People Who Became Victims of Violent Violence In The Last 12 Months By Sex	Proporsi Penduduk Yang Menjadi Korban Kejahatan Kekerasan Dalam 12 Bulan Terakhir Menurut Jenis Kelamin	1309
Proportion of Population Who Became Victims of Violent Violence in the Last 12 Months by Province	Proporsi Penduduk Yang Menjadi Korban Kejahatan Kekerasan Dalam 12 Bulan Terakhir Menurut Provinsi	1311
Proportion of Population Who Became Victims of Violent Violence In The Last 12 Months By Region Classification	Proporsi Penduduk Yang Menjadi Korban Kejahatan Kekerasan Dalam 12 Bulan Terakhir Menurut Klasifikasi Wilayah	1308
Unemployment Rate by Sex	Tingkat Pengangguran Terbuka Berdasarkan Jenis Kelamin	1177

Number of Companies Implementing SNI ISO 14001 Certification	Jumlah Perusahaan yang Menerapkan Sertifikasi SNI ISO 14001	1744
Number of Public Facilities that Implement Community Service Standards (SPM) and Registered	Jumlah Fasilitas Publik yang Menerapkan Standar Pelayanan Masyarakat (SPM) dan Teregister	1748
Number of Registered Green Products	Jumlah Produk Ramah Lingkungan yang Teregister	1746

Number of Deaths, Disappeared, and Hurt Victims Affected	Jumlah Korban Meninggal, Hilang, dan Terluka Terkena Dampak Bencana	1804
Number of Deaths, Disappeared, and Hurt Victims Affected by 100,000 People	Jumlah Korban Meninggal, Hilang, dan Terluka Terkena Dampak Bencana Per 100.000 Orang	1246

Number of Water Conservation Areas	Jumlah Kawasan Konservasi Perairan	1289
Proportion of catches of fish species that are within safe biological limits	Proporsi Tangkapan Jenis Ikan yang Berada Dalam Batasan Biologis yang Aman	1586

Number of Endangered Animals	Jumlah Satwa Terancam Punah	1297

Anti-Corruption Behaviour Index (ACBI) by Age Group	Indeks Perilaku Anti Korupsi (IPAK) Menurut Kelompok Umur	1499
Anti-Corruption Behaviour Index (ACBI) by Dimension	Indeks Perilaku Anti Korupsi (IPAK) Menurut Dimensi	635
Anti-Corruption Behaviour Index (ACBI) by Dimension and Age Group	Indeks Perilaku Anti Korupsi (IPAK) Menurut Dimensi dan Kelompok Umur	594
Anti-Corruption Behaviour Index (ACBI) by Dimension and Level of Education	Indeks Perilaku Anti Korupsi (IPAK) Menurut Dimensi dan Jenjang Pendidikan	597
Anti-Corruption Behaviour Index (ACBI) by Dimension and Sex	Indeks Perilaku Anti Korupsi (IPAK) Menurut Dimensi dan Jenis Kelamin	592
Anti-Corruption Behaviour Index (ACBI) by Dimension Urban-Rural Classification	Indeks Perilaku Anti Korupsi (IPAK) Menurut Dimensi dan Daerah Tempat Tinggal	595
Anti-Corruption Behaviour Index (ACBI) by Level of Education	Indeks Perilaku Anti Korupsi (IPAK) Menurut Jenjang Pendidikan	1504
Anti-Corruption Behaviour Index (ACBI) by Urban-Rural Classification	Indeks Perilaku Anti Korupsi (IPAK) Menurut Daerah Tempat Tinggal	1501
Household Poporsi Who Has Child Age 1-17 Years Who Have Physical Sentence And / Or Psychological Aggression From The Caregiver In The Last Year By Region Of Residence	Poporsi Rumah Tangga Yang Memiliki Anak Umur 1-17 Tahun Yang Mengalami Hukuman Fisik Dan/Atau Agresi Psikologis Dari Pengasuh Dalam Setahun Terakhir Menurut Wilayah Tempat Tinggal	1392
Indonesia Democracy Index (IDI) by Indicators	Indeks Demokrasi Indonesia (IDI) Menurut Indikator	598
Indonesia Democracy Index (IDI) by Variables	Indeks Demokrasi Indonesia (IDI) Menurut Variabel	598
Indonesian Democracy Index (IDI) by Province	Indeks Demokrasi Indonesia (IDI) Menurut Provinsi	598
Number of Complaints Handling Human Rights Violations	Jumlah Penanganan Pengaduan Pelanggaran Hak Asasi Manusia	1240
Number of Murder Crimes cases in the past year	Jumlah Kasus Kejahatan Pembunuhan Pada Satu Tahun Terakhir	1306
Percentage of children who have birth certificate by Area of Residence	Persentase anak yang memiliki akta kelahiran Menurut Daerah Tempat Tinggal	1413
Percentage of children who have birth certificate by Province	Persentase anak yang memiliki akta kelahiran Menurut Provinsi	1412
Percentage of Compliance with the implementation of Public Service Law for Ministry/Institution	Persentase Kepatuhan pelaksanaan UU Pelayanan Publik untuk KL	1236
Percentage of coverage of birth certificate ownership among population 0-17 years old by province	Persentase cakupan kepemilikan akta kelahiran pada penduduk 0-17 tahun menurut provinsi	2014
Percentage of Population Age 0-17 With Birth Certificate Ownership (Bottom 40%), by Province	Persentase Penduduk Usia 0-17 Tahun Dengan Kepemilikan Akta Lahir (40% Terbawah), Menurut Provinsi	1570
Percentage of Population Age 0-17 With Birth Certificate Ownership (Lower 40%), According to Gender	Persentase Penduduk Usia 0-17 Tahun Dengan Kepemilikan Akta Lahir (40% Terbawah), Menurut Jenis Kelamin	1573
Percentage of Population Age 0-17 With Birth Certificate Ownership (Lower 40%), by Area Type	Persentase Penduduk Usia 0-17 Tahun Dengan Kepemilikan Akta Lahir (40% Terbawah), Menurut Daerah Tempat Tinggal	1487
Poporsi Rumah Tangga Yang Memiliki Anak Umur 1-17 Tahun Yang Mengalami Hukuman Fisik Dan/Atau Agresi Psikologis Dari Pengasuh Dalam Setahun Terakhir	Poporsi Rumah Tangga Yang Memiliki Anak Umur 1-17 Tahun Yang Mengalami Hukuman Fisik Dan/Atau Agresi Psikologis Dari Pengasuh Dalam Setahun Terakhir	1391
Prevalence of Violence Against Girls	Prevalensi Kekerasan Terhadap Anak Perempuan	1364
Prevalence of Violence Against Girls by Age	Proporsi laki-laki muda umur 18-24 tahun yang mengalami kekerasan seksual sebelum umur 18 tahun	1371
Prevalence of Violence Against Girls by Type of Violence	Prevalensi Kekerasan Terhadap Anak Laki-Laki	1369
Proportion of Households with 1-17 Years Old Children Who Have Physical Sentence And / Or Psychological Aggression From Caretakers In The Last Year	Proporsi Rumah Tangga Yang Memiliki Anak Umur 1-17 Tahun Yang Mengalami Hukuman Fisik Dan/Atau Agresi Psikologis Dari Pengasuh Dalam Setahun Terakhir	1313
Proportion of Households with Children Aged 1-17 Years Experiencing Physical Sentence And / Or Psychological Aggression From Caretakers In The Last Year By Territory	Proporsi Rumah Tangga Yang Memiliki Anak Umur 1-17 Tahun Yang Mengalami Hukuman Fisik Dan/Atau Agresi Psikologis Dari Pengasuh Dalam Setahun Terakhir Menurut Wilayah Tempat Tinggal	1314
Proportion of prisoners who exceed the period of detention of the entire number of prisoners	Proporsi tahanan yang melebihi masa penahanan terhadap seluruh jumlah tahanan	1191
Proportion of Safe Residents Walking Alone In The Area Where Its Healed	Proporsi Penduduk Yang Merasa Aman Berjalan Sendirian Di Area Tempat Tinggalnya	1312
The proportion of children under 5 years of age whose birth is recorded by civil registration agencies by Province	Proporsi anak umur di bawah 5 tahun yang kelahirannya dicatat oleh lembaga pencatatan sipil Menurut Provinsi	1410
The proportion of children under 5 years of age whose birth is recorded by civil registration agencies by sex	Proporsi anak umur di bawah 5 tahun yang kelahirannya dicatat oleh lembaga pencatatan sipil Menurut Jenis Kelamin	1411
The proportion of crime victims in the last 12 months reporting to the police	Proporsi Korban Kekerasan dalam 12 bulan terakhir yang Melaporkan Kepada Polisi	1187
The proportion of major government expenditures to approved budgets	Proporsi pengeluaran utama pemerintah terhadap anggaran yang disetujui	1235
The proportion of women and young men aged 18-24 years who experienced sexual violence before the age of 18 years	Proporsi perempuan dan laki-laki muda umur 18-24 tahun yang mengalami kekerasan seksual sebelum umur 18 tahun	1318

Growth of Non Oil and Gas Product Exports	Pertumbuhan Ekspor Produk Non Migas	1261
Percentage of Data Users Who Use BPS Data as The Basis for National Development Planning, Monitoring and Evaluation	Persentase Pengguna Data yang Menggunakan Data BPS Sebagai Dasar Perencanaan, Monitoring dan Evaluasi Pembangunan Nasional	1606
Percentage of subscribers served by fixed broadband internet access networks to total households, by province	Persentase pelanggan terlayani jaringan internet akses tetap pitalebar (fixed broadband) terhadap total rumah tangga, menurut provinsi	2015
Proportion of Debt and Debt Service to Export of Goods and Services	Proporsi Pembayaran Utang Dan Bunga (Debt Service) Terhadap Ekspor Barang Dan Jasa	1260
Proportion of Realization of Government Revenues to Gross Domestic Product	Proporsi Realisasi Pendapatan Pemerintah Terhadap Produk Domestik Bruto	1588
Proportion of Remittance Volume (In US Dollars) To Total GDP	Proporsi Volume Remitansi (Dalam US Dollars) Terhadap Total PDB	1258
Ratio of Tax Revenue to GDP	Rasio Penerimaan Pajak Terhadap PDB	1529


How to View SDGs data
Data table can be consumed using "data" Model, and 0000 Domain to display specific id var (refer to menu Dynamic Data documentation above).


**Endpoint:** `https://webapi.bps.go.id/v1/api/list/model/data/domain/0000/var/id_var_in_table_above/key/your_api_key/`
example: Number of Deaths, Disappeared, and Hurt Victims Affected

**Endpoint:** `https://webapi.bps.go.id/v1/api/list/model/data/domain/0000/var/1804/key/your_api_key/`

              

### Send a Sample Request


Special Data Dissemination Standard (SDDS)
List All SDDS Table
This service is used to displays all SDDS table, domain must be "0000"


**Endpoint:** `https://webapi.bps.go.id/v1/list`


### Parameter
Field	Type	Description
model	String	
Model to display sdds table is "sdds"

key	String	
Key app to access API


### Send a Sample Request


SDDS Table List
This table is updated annually without prior notice

Variable	Variable (id)	Model	Id Var
Wholesale Price Index (WPI) (2018=100)	Indeks Harga Perdagangan Besar (IHPB) Indonesia (2018=100)	data	1721
Number and Percentage of Employment and Unemployment	Jumlah dan Persentase Penduduk Bekerja dan Pengangguran	data	1953
Average of Net Wage/Salary	Rata-Rata Upah/Gaji	data	1521
Inflation by Personal Care and Other Services Group and Sub (2018=100)	Inflasi (2018=100) Menurut Kelompok dan Sub Kelompok 11 Perawatan Pribadi dan Jasa Lainnya	data	1904
Inflation by Provision of Food and Beverages / Restaurant Group and Sub (2018=100)	Inflasi (2018=100) Menurut Kelompok dan Sub Kelompok 10 Penyediaan Makanan dan Minuman / Restoran	data	1903
Penduduk Berumur 15 tahun ke atas menurut jenis kegiatan	Penduduk Berumur 15 tahun ke atas menurut jenis kegiatan	data	529
Value of Export Oil&Gas - Non Oil&Gas	Nilai Ekspor Migas-NonMigas	data	1753
[2010 Version] 3. Distribution of GDP at Current Market Prices by Expenditure	[Seri 2010] 3. Distribusi PDB Triwulanan Atas Dasar Harga Berlaku menurut Pengeluaran	data	110
[2010 Version] 4. Growth Rate of GDP at Constant Market Prices By Expenditure	[Seri 2010] 4. Laju Pertumbuhan PDB menurut Pengeluaran	data	108
Consumer Price Index of 90 City (General)	Indeks Harga Konsumen 90 Kota (Umum)	data	1709
Consumer Price Index of Foods, Beverages and Tobacco Group and Sub (2022=100)	Indeks Harga Konsumen (2022=100) Menurut Kelompok dan Sub Kelompok 01 Makanan, Minuman dan Tembakau	data	2212
Value of Import Oil&Gas - Non Oil&Gas	Nilai Impor Migas-NonMigas	data	1754
GDP Implicit Growth by Industry (2010=100)	[Seri 2010] Laju Implisit PDB Menurut Lapangan Usaha Seri 2010	data	105
Distribution of GDP at Current Market Prices by Industry (2010=100)	[Seri 2010] Distribusi PDB Menurut Lapangan Usaha Seri 2010 Atas Dasar Harga Berlaku	data	106
Growth Rate of GDP by Industry (2010=100)	[Seri 2010] Laju Pertumbuhan PDB Seri 2010	data	104
Consumer Price Index of Health Group and Sub (2022=100)	Indeks Harga Konsumen (2022=100) Menurut Kelompok dan Sub Kelompok 05 Kesehatan	data	2216
Consumer Price Index of 38 Province (2022=100)	Indeks Harga Konsumen 38 Provinsi (2022=100)	data	2261
Inflation by Food, Beverage and Tobacco Group and Sub (2018 = 100)	Inflasi (2018=100) Menurut Kelompok dan Sub Kelompok 01 Makanan, Minuman dan Tembakau	data	1890
Inflation by Clothing and Footwear Group and Sub (2018=100)	Inflasi (2018=100) Menurut Kelompok dan Sub Kelompok 02 Pakaian dan Alas Kaki	data	1894
Inflation by Housing, Water, Electricity and Household Fuel Group and Sub (2018=100)	Inflasi (2018=100) Menurut Kelompok dan Sub Kelompok 03 Perumahan, Air, Listrik dan Bahan Bakar Rumah Tangga	data	1895
Inflation by Equipments and Routine Household Maintenance Group and Sub (2018=100)	Inflasi (2018=100) Menurut Kelompok dan Sub Kelompok 04 Perlengkapan, Peralatan dan Pemeliharaan Rutin Rumah Tangga	data	1897
Inflation by Health Group and Sub (2018=100)	Inflasi (2018=100) Menurut Kelompok dan Sub Kelompok 05 Kesehatan	data	1898
Inflation by Transportation Group and Sub (2018=100)	Inflasi (2018=100) Menurut Kelompok dan Sub Kelompok 06 Transportasi	data	1899
Inflation by Information, Communication and Financial Services Group and Sub (2018=100)	Inflasi (2018=100) Menurut Kelompok dan Sub Kelompok 07 Informasi, Komunikasi dan Jasa Keuangan	data	1900
Inflation by Recreation, Sports and Culture Group and Sub (2018=100)	Inflasi (2018=100) Menurut Kelompok dan Sub Kelompok 08 Rekreasi, Olahraga dan Budaya	data	1901
Inflation by Education Group and Sub (2018=100)	Inflasi (2018=100) Menurut Kelompok dan Sub Kelompok 09 Pendidikan	data	1902
Source of Growth of GDP by Industry (2010=100)	[Seri 2010] Sumber Pertumbuhan PDB Menurut Lapangan Usaha Seri 2010	data	554
Mid Year Population	Jumlah Penduduk Pertengahan Tahun	data	1975
Population Growth Rate	Laju Pertumbuhan Penduduk	data	1976
Consumer Price Index of Transportation Group and Sub (2022=100)	Indeks Harga Konsumen (2022=100) Menurut Kelompok dan Sub Kelompok 06 Transportasi	data	2217
Consumer Price Index of Information, Communication and Financial Service Group and Sub (2022=100)	Indeks Harga Konsumen (2022=100) Menurut Kelompok dan Sub Kelompok 07 Informasi, Komunikasi dan Jasa Keuangan	data	2218
Consumer Price Index of Recreation, Sport and Culture Group and Sub (2022=100)	Indeks Harga Konsumen (2022=100) Menurut Kelompok dan Sub Kelompok 08 Rekreasi, Olahraga dan Budaya	data	2219
Consumer Price Index of Education Group and Sub (2022=100)	Indeks Harga Konsumen (2022=100) Menurut Kelompok dan Sub Kelompok 09 Pendidikan	data	2220
Consumer Price Index of Provision of Food and Beverages / Restaurant Group and Sub (2022=100)	Indeks Harga Konsumen (2022=100) Menurut Kelompok dan Sub Kelompok 10 Penyediaan Makanan dan Minuman / Restoran	data	2221
Unemployment Rate by Province	Tingkat Pengangguran Terbuka Menurut Provinsi	data	543
Consumer Price Index of Foods, Beverages and Tobacco Group and Sub (2018=100)	Indeks Harga Konsumen (2018=100) Menurut Kelompok dan Sub Kelompok 01 Makanan, Minuman dan Tembakau	data	1905
Consumer Price Index of Clothing and Footwear Group and Sub (2018=100)	Indeks Harga Konsumen (2018=100) Menurut Kelompok dan Sub Kelompok 02 Pakaian dan Alas Kaki	data	1906
Consumer Price Index of Housing, Water, Electricity and Household Fuel Group and Sub (2018=100)	Indeks Harga Konsumen (2018=100) Menurut Kelompok dan Sub Kelompok 03 Perumahan, Air, Listrik dan Bahan Bakar Rumah Tangga	data	1907
Consumer Price Index of Equipments and Routine Household Maintenance Group and Sub (2018=100)	Indeks Harga Konsumen (2018=100) Menurut Kelompok dan Sub Kelompok 04 Perlengkapan, Peralatan dan Pemeliharaan Rutin Rumah Tangga	data	1908
Consumer Price Index of Health Group and Sub (2018=100)	Indeks Harga Konsumen (2018=100) Menurut Kelompok dan Sub Kelompok 05 Kesehatan	data	1909
Consumer Price Index of Transportation Group and Sub (2018=100)	Indeks Harga Konsumen (2018=100) Menurut Kelompok dan Sub Kelompok 06 Transportasi	data	1910
Consumer Price Index of Information, Communication and Financial Service Group and Sub (2018=100)	Indeks Harga Konsumen (2018=100) Menurut Kelompok dan Sub Kelompok 07 Informasi, Komunikasi dan Jasa Keuangan	data	1911
Consumer Price Index of Recreation, Sport and Culture Group and Sub (2018=100)	Indeks Harga Konsumen (2018=100) Menurut Kelompok dan Sub Kelompok 08 Rekreasi, Olahraga dan Budaya	data	1912
Consumer Price Index of Education Group and Sub (2018=100)	Indeks Harga Konsumen (2018=100) Menurut Kelompok dan Sub Kelompok 09 Pendidikan	data	1913
Consumer Price Index of Provision of Food and Beverages / Restaurant Group and Sub (2018=100)	Indeks Harga Konsumen (2018=100) Menurut Kelompok dan Sub Kelompok 10 Penyediaan Makanan dan Minuman / Restoran	data	1915
Consumer Price Index of Personal Care and Other Services Group and Sub (2018=100)	Indeks Harga Konsumen (2018=100) Menurut Kelompok dan Sub Kelompok 11 Perawatan Pribadi dan Jasa Lainnya	data	1916
GDP by Industry (2010=100)	[Seri 2010] PDB Menurut Lapangan Usaha Seri 2010	data	65
Consumer Price Index of Clothing and Footwear Group and Sub (2022=100)	Indeks Harga Konsumen (2022=100) Menurut Kelompok dan Sub Kelompok 02 Pakaian dan Alas Kaki	data	2213
Consumer Price Index of Housing, Water, Electricity and Household Fuel Group and Sub (2022=100)	Indeks Harga Konsumen (2022=100) Menurut Kelompok dan Sub Kelompok 03 Perumahan, Air, Listrik dan Bahan Bakar Rumah Tangga	data	2214
Quaterly Large and Medium Manufacturing (2010=100)	IBS Triwulanan (2010=100)	data	89
Monthly Large and Medium Manufacturing (2010=100)	IBS Bulanan (2010=100)	data	88
[2010 Version] 1. GDP at Current Market Prices by Expenditure	[Seri 2010] 1. PDB Triwulanan Atas Dasar Harga Berlaku menurut Pengeluaran	data	1955
[2010 Version] 2. GDP at Constant Market Prices by Expenditure	[Seri 2010] 2. PDB Triwulanan Atas Dasar Harga Konstan menurut Pengeluaran	data	1956
Wholesale Price Index (WPI) of Indonesia (2023=100)	Indeks Harga Perdagangan Besar (IHPB) Indonesia (2023=100)	data	2498
Consumer Price Index of Equipments and Routine Household Maintenance Group and Sub (2022=100)	Indeks Harga Konsumen (2022=100) Menurut Kelompok dan Sub Kelompok 04 Perlengkapan, Peralatan dan Pemeliharaan Rutin Rumah Tangga	data	2215
Consumer Price Index of Personal Care and Other Services Group and Sub (2022=100)	Indeks Harga Konsumen (2022=100) Menurut Kelompok dan Sub Kelompok 11 Perawatan Pribadi dan Jasa Lainnya	data	2222
Indeks Harga Perdagangan Internasional (IHPI) 2010=100	Indeks Harga Perdagangan Internasional (IHPI) 2010=100	data	1722
Export Price Index (2023=100)	Indeks Harga Ekspor (2023=100)	data	2487
Import Price Index (2023=100)	Indeks Harga Impor (2023=100)	data	2490

How to View SDDS data
Data table can be consumed using "data" or "statictable" Model (check the table below), and 0000 Domain to display specific id var (refer to menu Dynamic Data documentation above). For more information about SDDS, click here


**Endpoint:** `https://webapi.bps.go.id/v1/api/list/model/Model_in_table_below/domain/0000/var/id_var_in_table_below/key/your_api_key/`
example: Value of Export Oil&Gas - Non Oil&Gas

**Endpoint:** `https://webapi.bps.go.id/v1/api/list/model/data/domain/0000/var/1753/key/your_api_key/`

              

### Send a Sample Request



## Statistical Classifications
There are two kind of classifications that WebAPI provides: Klasifikasi Baku Lapangan Usaha Indonesia (KBLI: 2009, 2015, 2017, and 2020) that based on International Standard Industrial Classification of All Economic Activities (ISIC), and Klasifikasi Baku Komoditi Indonesia (KBKI 2015). For more information, Click here

Detail of Statistical Classification
This service is used to displays detail of a statistical classification are shown on the website


**Endpoint:** `https://webapi.bps.go.id/v1/api/view`


### Parameter
Field	Type	Description
model	String	
Model that allowed:

Allowed values:

KBLI: "kbli2009", "kbli2015", "kbli2017", "kbli2020"

KBKI: "kbki2015"

lang	String	
Language to display

Default value: ind

Allowed values: "ind", "eng"

id	String	
statistical classification id to display

Example: kbli_2009_01, kbki_2020_012


key	String	
Key app to access API


### Send a Sample Request




### Success Response
```json
{
  "status": "OK",
  "data-availability": "available",
  "data": [
    {
      "page": x,
      "pages": x,
      "per_page": x,
      "count": x,
      "total": x
    },
    [
      {
        "_index": "...",
        "_type": "...",
        "_id": "kbli_2020_011",
        "_score": x,
        "_source": {
          "konten": "...",
          "jenis": "...",
          "id": "...",
          "source": "Metadata Management System (MMS)",
          "judul": "...",
          "title": "...",
          "deskripsi": "...",
          "description": "...",
          "isbn": x,
          "issn": x,
          "no_katalog": x,
          "no_publikasi": x,
          "last_update": "date",
          "tgl_rilis": "date",
          "lokasi": null,
          "url": "https://www.bps.go.id/klasifikasi/app/view/model/code",
          "level": "...",
          "mfd": null,
          "sebelumnya": [
            {
            ...,
              "kode": "...",
              "judul": "...",
              "deskripsi": "..."
            },
            ...
          ],
          "turunan": [
            {
              ...,
              "kode": "...",
              "deskripsi": "...",
              "judul": "..."
            },
            ...

          ],
          "flag": ...,
          "tags": [
            ...,
            "...",
            ...
          ]
        }
      }
    ]
  ]
}
```


### Error 4xx
Name	Description
UserNotFound	
The id of the User was not found.



### Error Response
```http
HTTP/1.1 404 Not Found
  {
    "error": "UserNotFound"
  }
```

List of Statistical Classification
This service is used to list all of the statistical classification


**Endpoint:** `https://webapi.bps.go.id/v1/api/list/`


### Parameter
Field	Type	Description
model	String	
Model that allowed:

Allowed values:

KBLI: "kbli2009", "kbli2015", "kbli2017", "kbli2020"

KBKI: "kbki2015"

page optional	Number	
Page to display statistical classification

Allowed values: 1, 2, 3, 4, ..., n

per page optional	Number	
Number of statistical classification to display

level optional	String	
level of item

KBLI: kategori, golongan pokok, golongan, subgolongan, kelompok

KBKI: seksi, divisi, kelompok, kelas, subkelas, kelompok komoditas, kelompok

key	String	
Key app to access API


### Send a Sample Request



### Success Response
```json
{
  "status": "OK",
  "data-availability": "available",
  "data": [
    {
      "page": 1,
      "pages": 2710,
      "per_page": 1,
      "count": 1,
      "total": 2710
    },
    [
      {
        "_index": "datacontent",
        "_type": "_doc",
        "_id": "kbli_2020_01",
        "_score": null,
        "_source": {
          "konten": "...",
          "jenis": "...",
          "id": "klasifikasi_tahun_kode",
          "source": "Metadata Management System (MMS)",
          "judul": "...",
          "title": "...",
          "deskripsi": "...",
          "description": "...",
          "isbn": null,
          "issn": null,
          "no_katalog": null,
          "no_publikasi": null,
          "last_update": "date",
          "tgl_rilis": "date",
          "lokasi": null,
          "url": "https://www.bps.go.id/klasifikasi/app/view/klasifikasi/kode",
          "level": "...",
          "mfd": null,
          "sebelumnya": [
            {
              "kode": "...",
              "judul": "...",
              "deskripsi": "..."
            }
          ],
          "turunan": [
            ...,
            {
              "kode": "...",
              "deskripsi": "...",
              "judul": "..."
            },
            ...
          ],
          "flag": true,
          "tags": [
            ...,
            "...",
            ...
          ]
        },
        "sort": [
          "..."
        ]
      }
    ]
  ]
}
```


### Error 4xx
Name	Description
UserNotFound	
The id of the User was not found.



### Error Response
```http
HTTP/1.1 404 Not Found
  {
    "error": "UserNotFound"
  }
```


## Searching
This service is used to search website contents


**Endpoint:** `https://webapi.bps.go.id/v1/api/list/`


### Parameter
Field	Type	Description
model	String	
Model that user wants to search

lang optional	String	
Language to display strategic indicators

Default value: ind

Allowed values: "ind", "eng"

domain	Number	
Domains that will be displayed derived period data (see master domain)

Size range: 4

page	Number	
Page to display contents

Allowed values: 1, 2, 3, 4, ..., n

key	String	
Key app to access API

keyword optional	String	
Keyword to search. (Use "+" symbol if you have space on your keyword)


### Send a Sample Request



## News

## Detail News
This service is used to display detail of news


**Endpoint:** `https://webapi.bps.go.id/v1/view`


### Parameter
Field	Type	Description
domain	Number	
Domains that will be displayed news (see master domain)

Size range: 4

model	String	
Model to display news (news) for news is "news"

lang	String	
Language to display news

Default value: ind

Allowed values: "ind", "eng"

id	Number	
news id to display

Allowed values: 1, 2, 3, 4, ..., n

key	String	
Key app to access API


### Send a Sample Request



### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status of list news.

data	Object	
Information status

  news_id	Number	
ID unique of news

  newscat_id	String	
ID of news category

  title	String	
Title of news

  news	String	

## News

  rl_date	String	
Release Date of news

  picture	String	
Picture of news if available



### Success Response
```http
HTTP/1.1 200 OK
{
  "status": "OK",
  "data-availability": "available",
  "data":{
         "news_id":"news-890232",
         "newscat_id": "Statistik Lain",
         "title": "1212 1212 314",
         "news": "Saat ini telah dilaksanakan Sensus Ekonomi 2016 tahap kedua.",
         "rl_date":"2016-09-01",
         "picture" : "http://jabar-dev.bps.go.id/new/website/galeri/"
     }         
}
```


### Error 4xx
Name	Description
UserNotFound	
The id of the User was not found.



### Error Response
```http
HTTP/1.1 404 Not Found
  {
    "error": "UserNotFound"
  }
```


## List All BPS News
This service is used to displays all BPS News are shown on the website


**Endpoint:** `https://webapi.bps.go.id/v1/list`


### Parameter
Field	Type	Description
model	String	
Model to display news (news) for news is "news"

lang optional	String	
Language to display news

Default value: ind

Allowed values: "ind", "eng"

domain	Number	
Domains that will be displayed news (see master domain)

Size range: 4

page optional	Number	
Page to display news

Allowed values: 1, 2, 3, 4, ..., n

newscat optional	String	
News Category to display news

Allowed values: "sensus", "survey", "lainnya"

month optional	Number	
Month selected to display news

Allowed values: "01", "02", "03", "04", "12"

year optional	Number	
Year selected to display news

Allowed values: 1, 2, 3, 4, ..., n

keyword optional	String	
Keyword to search

key	String	
Key app to access API


### Send a Sample Request



### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status of list news.

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  1	Object	
List news

    news_id	Number	
ID unique of news

    newscat_id	String	
ID of news category

    newscat_name	String	
Name of news category

    title	String	
Title of news

    news	String	

## News

    rl_date	String	
Release Date of news



### Success Response
```http
HTTP/1.1 200 OK
   {
  "status": "OK",
  "data-availability": "available",
   "data": [
       {
           "page": 0,
           "pages": 1,
           "per_page": 10,
           "count": 3,
           "total": 3
       },
       [
           {
               "news_id": 9,
               "newscat_id": "Sensus dan Survey",
               "newscat_name": "KEGIATAN STATISTIK",
               "title": "tes berita OK",
               "news": "tes berita.....",
               "rl_date": "2016-12-27"
           },
          {
               "news_id": 4,
               "newscat_id": "Statistik Lain",
               "newscat_name": "KEGIATAN STATISTIK LAINNYA",
               "title": "Apel Siaga Sensus Ekonomi 2016 Jawa Barat",
               "news": "Apel siaga yang dilaksanakan pada Minggu pagi tanggal 28 Februari 2016 dipimpin oleh Gubernur Jawa Barat Ahmad \r\nHeryawan (Aher) di Halaman Gedung \r\nSate, Jl. Diponegoro No. 22, Kota Bandung......",
               "rl_date": "2016-02-28"
           },
           {
               "news_id": 2,
               "newscat_id": "Sensus dan Survey",
               "newscat_name": "KEGIATAN STATISTIK",
               "title": "Perubahan Tahun Dasar PDB Indonesia Berbasis SNA 2008",
               "news": "Perubahan tahun dasar Produk Domestik Bruto (PDB) merupakan suatu proses\r\n yang lazim dilakukan oleh kantor statistik suatu negara untuk \r\nmenggambarkan kondisi perekonomian terkini. BPS telah melakukan \r\nperubahan tahun dasar PDB sebanyak 5 (lima) kali yaitu pada tahun 1960, \r\n1973, 1983, 1993, dan 2000. Saat ini, BPS sedang melakukan proses \r\npenyusunan perubahan tahun dasar PDB dari tahun 2000 m.....",
               "rl_date": "2014-12-31"
           }
       ]
  ]
}
```


### Error 4xx
Name	Description
UserNotFound	
The id of the User was not found.



### Error Response
```http
HTTP/1.1 404 Not Found
  {
    "error": "UserNotFound"
  }
```


## List News Category
This service is used to display list of news category


**Endpoint:** `https://webapi.bps.go.id/v1/api/list`


### Parameter
Field	Type	Description
model	String	
Model to display list news category (newscategory) for news is "newscategory"

lang optional	String	
Language to display news category

Default value: ind

Allowed values: "ind", "eng"

domain	Number	
Domains that will be displayed news (see master domain)

Size range: 4

key	String	
Key app to access API


### Send a Sample Request



### Success 200
Field	Type	Description
status	String	
Return status, OK if success and Error if any error occured.

data-availability	String	
Availability status of list news.

data	Object[]	
Response Data

  0	Object	
Information status

    page	Number	
Information page

    pages	Number	
Information total page

    per_page	Number	
sum of per page

    count	Number	
count on this return list

    total	Number	
total page

  1	Object	
List news category

    newscat_id	Number	
ID unique of news

    newscat_name	String	
Name of news category



### Success Response
```http
HTTP/1.1 200 OK
{
  "status": "OK",
  "data-availability": "available",
  "data": [
       {
           "page": 1,
           "pages": 1,
           "per_page": 10,
           "count": 2,
           "total": 2
       },
       [
         {
           "newscat_id": "Sensus dan Survey",
           "newscat_name": "KEGIATAN STATISTIK"
           },
           {
           "newscat_id": "Statistik Lain",
           "newscat_name": "KEGIATAN STATISTIK LAINNYA"
           }
       ] 
   ]     
}
```


### Error 4xx
Name	Description
UserNotFound	
The id of the User was not found.



### Error Response
```http
HTTP/1.1 404 Not Found
  {
    "error": "UserNotFound"
  }
```
