# Architecture Flowchart

## System Architecture Diagram

```mermaid
flowchart TD
    A["Client<br/>(Postman / Browser)"] -->|"HTTP GET Request"| B["Flask Backend Server<br/>(Port 5000)"]
    
    B --> C{"API Routes Layer"}
    
    C -->|"/getData?disease=..."| D["getData Handler"]
    C -->|"/getInsights?disease=..."| E["getInsights Handler"]
    C -->|"/compare?disease1=...&disease2=..."| F["compare Handler"]
    
    D --> G{"Disease Router"}
    E --> H["Insights Service"]
    F --> H
    
    G -->|"covid"| I["COVID Service<br/>(Real-Time)"]
    G -->|"tb / dengue / malaria"| J["Disease Service<br/>(Historical)"]
    
    H --> I
    H --> J
    
    I -->|"HTTP GET"| K["disease.sh API<br/>Real-Time Data"]
    J -->|"File Read"| L["CSV Datasets<br/>Historical Data"]
    
    L --> L1["tb_data.csv"]
    L --> L2["dengue_data.csv"]
    L --> L3["malaria_data.csv"]
    
    I --> M{"Processing Layer"}
    J --> M
    
    M --> M1["Data Cleaning<br/>& Validation"]
    M --> M2["Trend Calculation<br/>% Change"]  
    M --> M3["Risk Classification<br/>High / Medium / Low"]
    
    M1 --> N["JSON Response"]
    M2 --> N
    M3 --> N
    
    N -->|"Structured JSON"| A

    style A fill:#4A90D9,stroke:#2C5F8A,color:#fff
    style B fill:#2ECC71,stroke:#1A8A4A,color:#fff
    style C fill:#F39C12,stroke:#C67E0A,color:#fff
    style K fill:#E74C3C,stroke:#B73A2E,color:#fff
    style L fill:#9B59B6,stroke:#7A3F94,color:#fff
    style N fill:#1ABC9C,stroke:#138D73,color:#fff
```

## Data Flow Description

### 1. Request Phase
- Client sends HTTP GET request to one of the three API endpoints
- Flask routes the request to the appropriate handler

### 2. Data Retrieval Phase
- **COVID-19**: Fetches live data from `disease.sh/v3/covid-19/all` and `/historical/all`
- **TB / Dengue / Malaria**: Loads data from CSV files using Pandas

### 3. Processing Phase
- **Data Cleaning**: Parse dates, handle missing values, sort chronologically
- **Trend Calculation**: Compute percentage change over recent periods
- **Risk Classification**: Assign High (>20%), Medium (5-20%), Low (<5%) risk levels

### 4. Response Phase
- Returns structured JSON with total cases, deaths, time-series, trends, and risk levels
