# Forms warehouse + Member 360 — ERD (2026-08-06)

Two views: the data-flow (how a submission travels) and the entity diagram (keys and joins).
Solid = live · dashed = designed, not yet built (P1–P3 persona wiring).

## 1. Data flow

```mermaid
flowchart LR
  subgraph SOURCES["Typeform (any number of forms)"]
    TF1["Census 2026\nDFeK5yop"]
    TF2["Application v3\nFsVHzNN9"]
    TF3["Honorary · legacy censuses\nmkUJqsfM · I409BFlj · DXs5mhZn"]
    TFN["your next form\n(one config line)"]
  end

  subgraph OPS["Operational copy (curated)"]
    MAKE["Make 4860042\nwebhook, instant"]
    ATF["Airtable Forms table\n~760 cols · 58 census fields\nForm ID = Annual Census 2026"]
    ATM["Airtable Members\nMost Recent Revenue (lookup)"]
    SLACK["#automation-tests\nno-match alert"]
  end

  subgraph WH["Supabase warehouse (complete, append-only)"]
    LOADER["sync_form_responses.py\nGH Action daily 13:47 UTC"]
    FR[("form_responses\n1 row / submission\nanswers jsonb — 9 cols forever")]
    MAP[("form_field_map\nref → canonical_key\nDATA, not schema")]
    WIN["form_windowed()\nlatest per member×key\nin a time window\nPII excluded"]
  end

  subgraph DOORS["Gated doors (gate 232)"]
    FS["form_stats\naggregates only · %\ncells<3 suppressed"]
    MFA["my_form_answers\nself only"]
    FFH["form_field_history\nself only, over time"]
  end

  OLIVIA["Olivia loop\n(staging 9b14c44c,\nawaiting promote)"]

  TF1 --> MAKE --> ATF --> ATM
  MAKE -. "0 or 2+ email matches" .-> SLACK
  TF1 --> LOADER --> FR
  TF2 --> LOADER
  TF3 --> LOADER
  TFN --> LOADER
  FR --> WIN
  MAP --> WIN
  WIN --> FS & MFA & FFH --> OLIVIA

  subgraph P360["Member 360 / personas"]
    MA[("member_attributes\npersona + matching surface")]
    CI[("content_items\nsearch index + embeddings")]
    DOS["member_dossier_v2\npersonalization"]
  end
  WIN -. "P1: niche/brands/skus\nnewest wins" .-> MA
  FR -. "P2: census long-text\n(your exposure call)" .-> CI
  FFH -. "P3: own-census section" .-> DOS
```

## 2. Entities and keys

```mermaid
erDiagram
  FORM_RESPONSES {
    text token PK "Typeform response token"
    text form_id "DFeK5yop etc"
    text member_at_id FK "stamped, null = unmatched"
    text email "typed, lowercased"
    timestamptz submitted_at "the decay axis"
    jsonb answers "ref to q-t-v"
    jsonb raw "full payload"
  }
  FORM_FIELD_MAP {
    text form_id PK
    text ref PK
    text canonical_key "ttm_revenue, main_niche, ..."
  }
  MEMBER_PROFILES {
    text at_member_id PK
    jsonb at_fields "AT mirror incl Preferred Email"
  }
  MEMBER_ATTRIBUTES {
    text at_member_id PK
    text main_niche
    text rev_band
    text[] chapter_affiliation
  }
  MEMBERS {
    text phone PK "WhatsApp layer only"
    text at_member_id FK
  }
  CONTENT_ITEMS {
    text source "fb, wa, application (census planned)"
    vector embedding
  }
  EVENT_REGISTRATIONS_LIVE {
    text roster_record_id PK
    text event_at_id FK
    text member_at_id FK
  }
  EVENTS_CATALOG {
    text at_record_id PK
  }
  OLIVIA_MESSAGES {
    text phone FK
    text role
  }

  FORM_RESPONSES }o--|| MEMBER_PROFILES : "stamped by unique email"
  FORM_RESPONSES }o--o| FORM_FIELD_MAP : "form_id + ref"
  MEMBER_PROFILES ||--|| MEMBER_ATTRIBUTES : "derived nightly"
  MEMBERS }o--|| MEMBER_ATTRIBUTES : "phone layer"
  EVENT_REGISTRATIONS_LIVE }o--|| EVENTS_CATALOG : "event_at_id"
  EVENT_REGISTRATIONS_LIVE }o--|| MEMBER_ATTRIBUTES : "member_at_id"
  OLIVIA_MESSAGES }o--|| MEMBERS : "phone"
  CONTENT_ITEMS }o--o| MEMBER_ATTRIBUTES : "author / access rules"
```

Notes: Airtable = curated operational copy (team + lookups); Supabase = complete raw archive +
everything machines reason over. `form_responses` is append-only — change-over-time is a read
(`form_field_history`), never an update. Exposure: raw answers owner-only; aggregates % with
small-cell suppression (whale-rule floor 3).
