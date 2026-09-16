# FarmMesh AI --- Product Requirements Document (PRD)

**Working title:** FarmMesh AI\
**Category:** AI-powered agricultural marketplace / farm commerce
platform\
**Primary market:** India, with an initial focus on small and
micro-scale horticulture producers\
**Document status:** Hackathon MVP PRD — updated product architecture\
**Version:** 0.2\
**Last updated:** 2026-09-15

------------------------------------------------------------------------

## 1. Executive Summary

FarmMesh AI is a **role-aware agricultural marketplace website** for India.

The product has two deliberately different experiences:

1. **Standard user / buyer**
   - Signs up with email.
   - Completes a lightweight profile: name, age/date-of-birth where required, location and preferences.
   - Uses a conventional marketplace to browse agricultural products, search, filter, view listings and place orders.
   - Does **not** receive the vendor-only AI farm tools.

2. **Vendor / farmer**
   - Signs up with email.
   - Completes the same basic profile and explicitly selects **"I am a farmer/vendor"** during onboarding.
   - Receives the standard marketplace **plus a vendor workspace containing AI-assisted tools**.
   - Can create produce listings, analyze harvest images, generate descriptions, receive price guidance, find buyers, aggregate supply, optimize logistics and access market-intelligence features.

The central product idea is therefore:

> **A normal agricultural marketplace for everyone, with an AI commerce and market-intelligence layer unlocked for farmers/vendors.**

The original FarmMesh concept remains focused on fragmented small-farm supply: small quantities, weak buyer discovery, inconsistent demand visibility, logistics costs and poor price discovery. fileciteturn0file0L14-L24

The added market-intelligence direction from the AMIE specification is incorporated as a **vendor-only intelligence module**. It uses historical/current market evidence, farmer state, buyer demand and infrastructure/network state to forecast possible supply-demand imbalance, identify bottlenecks, simulate scenarios and recommend actions. The source specification explicitly describes this chain as state estimation → forecasting → imbalance detection → bottleneck discovery → simulation → intervention optimization. fileciteturn0file1L11-L43

### Product principle

FarmMesh should not force every marketplace user through an AI workflow.

The product should feel like:

```text
                         FARMESH
                            │
                 ┌──────────┴──────────┐
                 │                     │
          STANDARD USER          FARMER / VENDOR
                 │                     │
                 ▼                     ▼
        NORMAL MARKETPLACE      NORMAL MARKETPLACE
                                       +
                                AI VENDOR WORKSPACE
                                       │
                   ┌───────────────────┼───────────────────┐
                   ▼                   ▼                   ▼
             Harvest AI         Market Intelligence   Farm Planning
                   │                   │                   │
                   ▼                   ▼                   ▼
             Listing / Price    Forecast / Risk       Crop Advice
                   │                   │                   │
                   └───────────────────┼───────────────────┘
                                       ▼
                                  MARKETPLACE
                                       │
                                       ▼
                               Buyers / Orders
```

### Core proposition

> **Let everyone buy and discover agricultural products normally. Give farmers/vendors an AI layer that helps them decide what to sell, how to price it, who to sell to, how to aggregate it, and what to grow next.**

------------------------------------------------------------------------

# 2. Problem Statement

## 2.1 Farmer-side problems

Small farmers and household-scale growers face several structural
problems:

-   They produce relatively small quantities.
-   Wholesale buyers often prefer larger, predictable volumes.
-   Market prices can vary substantially by location and time.
-   Farmers may have limited visibility into downstream demand.
-   Finding individual restaurants, retailers, processors, and consumers
    is difficult.
-   Transport costs can make small orders uneconomical.
-   Produce is perishable, creating time pressure.
-   Quality and grading are often inconsistent.
-   Digital listing and marketing require time and technical knowledge.
-   Farmers frequently make production decisions without reliable local
    demand signals.

## 2.2 Buyer-side problems

Restaurants, retailers, small supermarkets, processors, and consumers
face the inverse problem:

-   Finding reliable local suppliers takes time.
-   Small farmers may not provide consistent quantities.
-   Quality is difficult to verify before purchase.
-   Multiple suppliers may be required to fulfill one order.
-   Procurement from many small farms creates administrative overhead.
-   Last-mile collection can be inefficient.

## 2.3 Market failure

The system has a **fragmentation problem**:

``` text
Farmer A ── 20 kg ─┐
Farmer B ── 35 kg ─┤
Farmer C ── 15 kg ─┼── fragmented supply
Farmer D ── 30 kg ─┤
Farmer E ── 25 kg ─┘

                 ↓

          AI aggregation

                 ↓

             125 kg

                 ↓

       Restaurant / Retailer
```

FarmMesh's purpose is to create the digital coordination layer between
these fragmented producers and buyers.

------------------------------------------------------------------------

# 3. Product Vision

## Vision

Create a **digital commerce operating system for small agricultural
producers**.

The platform should make selling agricultural produce feel as simple as
listing a product on a social-commerce marketplace.

### Long-term vision

``` text
                 FARMER
                    │
             Capture / Voice
                    │
                    ▼
             AI FARM COPILOT
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
    PRODUCE       MARKET       PLANNING
    ANALYSIS      DEMAND       ADVICE
       │            │            │
       └────────────┼────────────┘
                    ▼
              MARKETPLACE
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       Consumer  Restaurant  Retailer
          │         │         │
          └─────────┼─────────┘
                    ▼
             AI LOGISTICS
                    │
                    ▼
              FARMER PAYOUT
```

------------------------------------------------------------------------

# 4. Goals

## 4.1 Primary goals

1.  Make selling small quantities of produce simple.
2.  Increase buyer access for micro-farmers.
3.  Aggregate fragmented supply.
4.  Improve farmer price discovery.
5.  Match supply with local demand.
6.  Reduce unnecessary logistics costs.
7.  Provide AI-assisted crop and sales recommendations.
8.  Support regional languages and low-literacy workflows.
9.  Build a compelling end-to-end hackathon demonstration.

## 4.2 Secondary goals

-   Create transparent farmer earnings.
-   Build a farmer reputation system.
-   Create demand forecasts.
-   Enable recurring buyer relationships.
-   Create structured agricultural supply data.

## 4.3 Non-goals for the MVP

Do **not** attempt to build:

-   A full banking system.
-   Agricultural loans.
-   Insurance underwriting.
-   Autonomous farm machinery.
-   A complete ERP for large farms.
-   Nationwide logistics.
-   High-precision agronomic diagnosis.
-   Full commodity trading.
-   A replacement for regulated agricultural markets.

------------------------------------------------------------------------

# 5. Target Users

## 5.0 Authentication and Role-Based Onboarding

### Entry point

All users begin with the same email-based account creation flow:

```text
Landing Page
    ↓
Sign up with email
    ↓
Verify email
    ↓
Complete basic profile
    ├── Name
    ├── Age / date of birth (only where product/legal requirements justify it)
    ├── Location
    └── Preferred language
    ↓
Are you a farmer/vendor?
    ├── No → Standard Marketplace
    └── Yes → Vendor Marketplace + AI Workspace
```

### Role selection

The onboarding question should be explicit:

> **Are you a farmer/vendor?**
>
> ○ No, I'm a buyer/customer  
> ○ Yes, I'm a farmer/vendor

The role controls access to vendor-only features.

### Standard user experience

A standard user sees:

- Marketplace home.
- Search and category browsing.
- Product/listing details.
- Cart/order flow.
- Order history.
- Profile.
- Favorites/saved listings.
- Buyer-side purchase requirements where applicable.

### Vendor experience

A vendor sees everything in the standard marketplace plus:

- Vendor dashboard.
- Farm/vendor profile.
- Create/manage produce listings.
- AI harvest analysis.
- AI listing generation.
- AI price recommendation.
- Buyer matching.
- Supply aggregation.
- Logistics estimation.
- Market intelligence.
- Demand/price outlook.
- Crop recommendation.
- Vendor AI copilot.

### Authorization rule

Role gating must be enforced **server-side**, not only by hiding UI components.

```text
STANDARD_USER
    → marketplace APIs

VENDOR
    → marketplace APIs
    → vendor APIs
    → AI APIs
    → market-intelligence APIs

ADMIN
    → administrative APIs
```

A user changing browser state, calling an endpoint directly, or modifying a client-side role flag must not gain vendor privileges.

### Role changes

For the MVP, a user can request a role change from standard user to vendor. The backend should validate the request and create the required vendor/farm profile.

Do not rely on a client-provided `role="vendor"` field as proof of authorization.

------------------------------------------------------------------------

## 5.1 Primary: Small farmer / micro-farmer

Typical characteristics:

-   Small landholding or garden-scale production.
-   Produces vegetables, fruits, herbs, flowers, or spices.
-   May use a smartphone.
-   May prefer voice over typing.
-   Needs quick selling rather than complex enterprise software.

### Example

**Ravi**

-   Farm: 0.5 acre
-   Location: Kerala
-   Produce: chilli, tomato, beans
-   Problem: sells mostly through a local intermediary
-   Goal: obtain better net realization without spending hours searching
    for buyers.

------------------------------------------------------------------------

## 5.2 Buyer: Restaurant

Needs:

-   Fresh produce.
-   Predictable quantity.
-   Delivery within a specific time window.
-   Consistent quality.
-   Recurring procurement.

------------------------------------------------------------------------

## 5.3 Buyer: Retailer

Needs:

-   Larger quantities.
-   Standardized grading.
-   Reliable supply.
-   Competitive pricing.

------------------------------------------------------------------------

## 5.4 Buyer: Consumer

Needs:

-   Local produce.
-   Freshness.
-   Trust.
-   Convenient ordering.
-   Simple delivery.

------------------------------------------------------------------------

## 5.5 Aggregator / collection center

Needs:

-   View nearby harvests.
-   Combine compatible lots.
-   Plan pickups.
-   Track quantities.
-   Manage quality.

------------------------------------------------------------------------

# 6. Product Principles

### 6.1 AI should reduce work, not add work

A farmer should not have to understand AI.

Bad:

> Select crop → select grade → enter quantity → select harvest date →
> write description → set price.

Better:

> Take a photo + say "30 kilos harvested today."

------------------------------------------------------------------------

### 6.2 Net income matters more than selling price

The platform must optimize:

**Farmer net = selling revenue − logistics − packaging − marketplace
fees − other applicable costs**

A higher selling price is not necessarily better if logistics costs are
much higher.

------------------------------------------------------------------------

### 6.3 Human-in-the-loop

AI recommendations should be presented as recommendations, not
guaranteed facts.

------------------------------------------------------------------------

### 6.4 Local-first

Initial design should prioritize:

-   Local buyers.
-   Local languages.
-   Local transport.
-   Local demand patterns.
-   Regional crops.

------------------------------------------------------------------------

# 7. Core Features

## Feature 1 --- AI Harvest Listing

### Description

Farmer uploads a crop image or speaks a short description.

### Input

-   Photo.
-   Voice.
-   Optional quantity.
-   Optional harvest date.

### AI output

``` json
{
  "crop": "green_chilli",
  "confidence": 0.96,
  "estimated_quality": "A",
  "visible_defects": [],
  "quantity_kg": 30,
  "harvest_date": "2026-09-13",
  "suggested_price_range": {
    "min": 55,
    "max": 72
  }
}
```

### UX

``` text
[ Take Photo ]

       ↓

AI identifies:
Green Chilli

       ↓

"How much do you have?"

[ 30 kg ]

       ↓

[ Create Listing ]
```

------------------------------------------------------------------------

# 8. Feature 2 --- AI Product Description Generator

The system automatically generates:

-   Product title.
-   Description.
-   Grade.
-   Harvest date.
-   Freshness statement.
-   Search keywords.
-   Multilingual listing.

### Example

Input:

> 30 kg chilli, harvested today.

Output:

> **Fresh Green Chilli --- Grade A**
>
> Harvested today. Suitable for restaurants, retailers, and household
> buyers.

The same listing can be rendered in English, Malayalam, Hindi, Tamil,
Kannada, etc.

------------------------------------------------------------------------

# 9. Feature 3 --- AI Quality / Grading

## Objective

Estimate visible quality from images.

### Possible model pipeline

``` text
Image
  │
  ▼
Image preprocessing
  │
  ▼
Crop classifier
  │
  ▼
Object / defect detection
  │
  ▼
Quality scoring
  │
  ▼
Grade recommendation
```

### MVP

Do not train a custom agricultural vision model from scratch.

Use:

-   A multimodal vision model for initial classification.
-   Rule-based checks.
-   Optional lightweight custom classifier for a small set of crops.

### Example quality factors

For vegetables:

-   Color uniformity.
-   Visible bruising.
-   Rot.
-   Pest damage.
-   Size consistency.
-   Surface damage.
-   Maturity.

### Important limitation

Image-based grading cannot reliably determine:

-   Internal damage.
-   Chemical residues.
-   Exact nutritional composition.
-   Microbial contamination.
-   Hidden spoilage.

Therefore:

> **AI grade = preliminary visual grade, subject to buyer/aggregator
> verification.**

------------------------------------------------------------------------

# 10. Feature 4 --- AI Price Recommendation

This is one of the most important AI components.

## Objective

Estimate a recommended price range rather than pretending there is one
"correct" price.

### Input features

``` text
Crop
Location
Date
Season
Estimated grade
Quantity
Recent local transaction prices
Wholesale prices
Buyer demand
Distance to buyer
Expected spoilage
Historical prices
Weather/event signals
```

### Output

``` text
Recommended price:
₹58–₹67/kg

Confidence:
Medium

Reason:
• Local demand is above average
• Grade A
• Recent prices trending upward
• Nearby restaurant demand is strong
```

## Model strategy

### MVP

Start with a weighted statistical model:

``` text
Predicted price =
    base_market_price
  + demand_adjustment
  + quality_adjustment
  + locality_adjustment
  + seasonality_adjustment
  - excess_supply_adjustment
```

Then upgrade to:

-   XGBoost / LightGBM
-   Random Forest
-   Temporal models if sufficient historical data exists.

### Avoid

Do not claim:

> "AI guarantees ₹70/kg."

Use:

> "Estimated market range: ₹62--₹69/kg."

------------------------------------------------------------------------

# 11. Feature 5 --- AI Buyer Matching

The system matches available produce with buyer requirements.

## Buyer profile

``` json
{
  "buyer_id": "B102",
  "type": "restaurant",
  "required_crop": "green_chilli",
  "quantity_kg": 50,
  "max_price": 75,
  "quality": "A",
  "delivery_window": "today_18:00-21:00",
  "location": "Kochi"
}
```

## Farmer listing

``` json
{
  "farmer_id": "F51",
  "crop": "green_chilli",
  "quantity_kg": 30,
  "quality": "A",
  "price": 64,
  "location": "Aluva"
}
```

## Matching score

Example:

``` text
Match Score =
    30% crop compatibility
  + 20% quantity compatibility
  + 15% price compatibility
  + 15% distance
  + 10% quality
  + 10% delivery-time compatibility
```

Weights should eventually be learned from successful transactions.

------------------------------------------------------------------------

# 12. Feature 6 --- AI Supply Aggregation

This is the feature that most strongly differentiates the platform.

Suppose:

``` text
Farmer A → 20 kg
Farmer B → 35 kg
Farmer C → 15 kg
Farmer D → 30 kg
```

A restaurant requires:

``` text
100 kg
```

The system creates a virtual aggregated lot.

### Algorithm

1.  Group listings by crop.
2.  Group by acceptable quality.
3.  Filter by geography.
4.  Filter by harvest freshness.
5.  Identify compatible quantities.
6.  Calculate collection cost.
7.  Calculate buyer revenue.
8.  Calculate farmer payout.
9.  Select the economically viable combination.

### Optimization objective

Maximize:

``` text
Total farmer payout
```

subject to:

``` text
Buyer quantity requirement
Quality constraints
Maximum delivery time
Vehicle capacity
Pickup radius
Perishability
```

This can be implemented using:

-   Greedy matching for MVP.
-   Integer Linear Programming later.
-   OR-Tools for route and allocation optimization.

------------------------------------------------------------------------

# 13. Feature 7 --- AI Logistics Optimization

## Objective

Reduce collection and delivery costs.

### Inputs

-   Farmer locations.
-   Quantities.
-   Buyer location.
-   Vehicle capacity.
-   Time windows.
-   Produce perishability.
-   Road/travel estimates.

### Output

``` text
Pickup Route

Farm A → Farm C → Farm D
              ↓
        Collection Hub
              ↓
         Restaurant B
```

### MVP

Use:

-   Google Maps / Mapbox routing API.
-   Haversine distance for rough filtering.
-   OR-Tools vehicle routing.

### Optimization

Minimize:

``` text
transport_cost
+ travel_time
+ spoilage_risk
```

subject to:

``` text
vehicle_capacity
delivery_window
pickup_window
```

------------------------------------------------------------------------

# 14. Feature 8 --- AI Crop Recommendation

This transforms the platform from a marketplace into a **farm planning
copilot**.

## Farmer asks

> "What should I grow next month?"

### Inputs

-   Location.
-   Available area.
-   Soil information.
-   Water availability.
-   Season.
-   Historical production.
-   Existing crops.
-   Expected harvest date.

### Market inputs

-   Historical demand.
-   Current supply.
-   Buyer requests.
-   Price trends.
-   Seasonal demand.
-   Local events/festivals.

### Output

``` text
Recommended crops

1. Green chilli
   Demand: High
   Expected harvest: 70–90 days
   Market risk: Medium

2. Beans
   Demand: Medium-High
   Expected harvest: 45–60 days
   Market risk: Medium

3. Tomato
   Demand: Medium
   Current local supply: High
   Recommendation: Reduce allocation
```

### Critical design principle

The model should not optimize only for price.

It should optimize:

``` text
Expected Profit
×
Probability of Successful Sale
```

A crop with a theoretical high price but uncertain demand may be worse
than a slightly lower-margin crop with reliable buyers.

------------------------------------------------------------------------

# 15. Feature 9 --- Demand Forecasting

## Objective

Predict future demand at a local level.

### Data sources

Potential sources include:

-   Historical platform orders.
-   Buyer purchase requests.
-   Marketplace searches.
-   Crop listings.
-   Historical market prices.
-   Seasonal patterns.
-   Festivals/events.
-   Weather data.
-   Public agricultural datasets.
-   Public market data where legally available.

### Forecast

``` text
Green chilli demand
Next 7 days: +18%
Next 30 days: +12%
Confidence: Medium
```

### Model progression

#### MVP

-   Moving averages.
-   Exponential smoothing.
-   Seasonal multipliers.
-   Rule-based festival adjustments.

#### Later

-   XGBoost.
-   Prophet-style models.
-   Temporal Fusion Transformer / other sequence models if enough data
    exists.

------------------------------------------------------------------------

# 16. Feature 10 --- Farmer AI Copilot

A conversational assistant that can answer:

> "What can I sell today?"

> "Why is the recommended price lower?"

> "Which crop should I plant next?"

> "Who is buying chilli near me?"

> "How much did I earn this month?"

> "Why did my listing not sell?"

### Architecture

``` text
Farmer
  │
  ▼
Voice / Text
  │
  ▼
Speech-to-Text
  │
  ▼
LLM Agent
  │
  ├── Marketplace database
  ├── Pricing engine
  ├── Demand model
  ├── Farmer profile
  ├── Order system
  └── Logistics engine
  │
  ▼
Action / Answer
```

The LLM should **not directly invent prices or inventory information**.

It should call structured backend functions.

------------------------------------------------------------------------

# 17. Feature 11 --- Multilingual Voice Interface

This is important for accessibility.

### Example

Farmer speaks in Malayalam:

> "ഇന്ന് മുപ്പത് കിലോ പച്ചമുളക് ഉണ്ട്."

Pipeline:

``` text
Malayalam speech
      ↓
Speech-to-text
      ↓
Intent extraction
      ↓
Marketplace action
      ↓
Malayalam response
```

Potential technology:

-   Whisper or managed speech recognition.
-   LLM multilingual understanding.
-   Text-to-speech for responses.

### MVP

Support:

1.  English
2.  Malayalam

Then expand.

------------------------------------------------------------------------

# 18. Feature 12 --- Farmer Reputation

Build trust without requiring traditional branding.

Metrics:

-   Order fulfillment rate.
-   Cancellation rate.
-   Buyer rating.
-   Quality consistency.
-   On-time handover.
-   Repeat buyer rate.

Example:

``` text
Ravi's Farm

★★★★★ 4.8

97% orders fulfilled
94% on-time
89% repeat buyers
```

Do not allow AI-generated reputation scores to become opaque or
punitive.

------------------------------------------------------------------------

# 19. Feature 13 --- Buyer Recurring Orders

Restaurants and retailers can create:

> "Buy 30 kg tomatoes every Monday, Wednesday, Friday."

The system can:

1.  Predict upcoming requirement.
2.  Reserve farmer supply.
3.  Aggregate supply.
4.  Schedule pickup.
5.  Alert if supply is insufficient.
6.  Suggest substitute suppliers.

------------------------------------------------------------------------

# 20. Feature 14 --- Produce Traceability

Each listing receives a lot ID.

``` text
LOT-KL-2026-00128
```

Track:

``` text
Farm
↓
Harvest
↓
Quality check
↓
Collection
↓
Buyer
↓
Delivery
```

For the MVP, a standard database is enough.

Blockchain is **not required**.

------------------------------------------------------------------------

# 21. AI Architecture

## High-level architecture

``` text
                       ┌─────────────────────┐
                       │   Mobile / Web App  │
                       └──────────┬──────────┘
                                  │
                            REST / WebSocket
                                  │
                       ┌──────────▼──────────┐
                       │     API Gateway     │
                       └──────────┬──────────┘
                                  │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
             ▼                    ▼                    ▼
      Marketplace Service   AI Orchestrator     Logistics Service
             │                    │                    │
             │             ┌──────┼───────┐            │
             │             ▼      ▼       ▼            │
             │          Vision  LLM    Forecast        │
             │             │      │       │            │
             └─────────────┼──────┼───────┘            │
                           │      │                    │
                           ▼      ▼                    ▼
                       PostgreSQL / Redis / Object Storage
```

------------------------------------------------------------------------

# 22. Recommended Tech Stack

The original PRD proposed Flutter for a farmer mobile app and Next.js for web. The revised product vision is **website-first**, so Flutter is not required for the MVP.

## Frontend

### Recommended

**Next.js + TypeScript**

Use for:

- Public landing page.
- Email authentication screens.
- Onboarding.
- Standard marketplace.
- Vendor dashboard.
- Vendor AI workspace.
- Buyer dashboard.
- Admin dashboard.
- Responsive mobile web experience.

### UI

- Tailwind CSS.
- shadcn/ui or a similarly accessible component system.
- React Hook Form for forms.
- Zod for client-side validation.
- TanStack Query for server-state management.

### Maps

Use **Mapbox GL JS** or **MapLibre** only where location visualization/routing is required.

A map should not be a mandatory part of the basic marketplace.

## Backend

**Python + FastAPI**

Use for:

- Authentication integration.
- User/profile APIs.
- Marketplace APIs.
- Vendor APIs.
- Listings.
- Orders.
- Matching.
- AI orchestration.
- Market intelligence.
- Forecasting.
- Optimization.

FastAPI is retained because the product combines normal web APIs with Python-based ML and optimization workloads. The original PRD also recommends FastAPI, Pydantic and SQLAlchemy. fileciteturn1file0L576-L605

## Database

**PostgreSQL**

Use for:

- Users.
- Roles.
- Vendor/farm profiles.
- Listings.
- Products/crops.
- Buyers.
- Orders.
- Transactions.
- Ratings.
- Market observations.
- Demand signals.
- Recommendations.

### Geospatial

**PostGIS**

Use only where required for:

- Nearby vendors.
- Nearby buyers.
- Pickup radius.
- Geographic filtering.
- Logistics calculations.

### Cache / background work

**Redis** is recommended but not mandatory on day one.

Use it for:

- Caching market data.
- AI response caching.
- Rate limiting.
- Background job coordination.

For a small MVP, do not add Redis merely because it appears in the architecture. Add it when asynchronous jobs, caching or rate limits justify it.

## Object storage

Use one S3-compatible provider:

- Supabase Storage for simplest MVP integration, or
- Cloudflare R2 / AWS S3 for more control.

Store:

- Crop photos.
- Vendor/farm images.
- User uploads.

Do not store large image binaries directly in PostgreSQL.

## Background jobs

For AI analysis, forecasting and optimization jobs that may take longer than a normal request:

**Celery + Redis** is a reasonable Python choice.

For a very small hackathon MVP, FastAPI background tasks can be used first, then moved to a worker queue when required.

## AI

Use a provider abstraction rather than coupling the entire application to one model vendor:

```text
AIProvider
├── GroqProvider
├── GeminiProvider
└── OptionalFallbackProvider
```

This makes it possible to change models without rewriting marketplace logic.

## ML / optimization

- Python
- pandas
- NumPy
- scikit-learn
- XGBoost where justified
- OR-Tools for aggregation/routing/optimization
- SciPy where useful

The AMIE specification recommends establishing simple baselines before adding complex ML and using chronological validation for time-series data. fileciteturn0file1L737-L841

## Deployment

Hackathon:

- Frontend → Vercel
- Backend → Render / Railway / equivalent
- PostgreSQL → Supabase / managed PostgreSQL
- Object storage → Supabase Storage / S3-compatible provider
- AI → Groq or Gemini API
- Maps → Mapbox/MapLibre if required

Production deployment can later move to AWS/GCP/Azure.

# 23. Backend

Recommended:

**Python + FastAPI**

Why:

-   Excellent AI/ML ecosystem.
-   Fast API development.
-   Pydantic validation.
-   Easy integration with ML models.
-   Async support.

Alternative:

-   Node.js + NestJS.

------------------------------------------------------------------------

# 24. Database

### Primary database

**PostgreSQL**

Store:

-   Users.
-   Farmers.
-   Farms.
-   Crops.
-   Listings.
-   Buyers.
-   Orders.
-   Transactions.
-   Ratings.
-   Demand signals.
-   Recommendations.

### Geospatial

Use:

**PostGIS**

for:

-   Nearby farmers.
-   Nearby buyers.
-   Pickup radius.
-   Geographic filtering.

### Cache

**Redis**

Use for:

-   Sessions.
-   Frequently requested market prices.
-   Search results.
-   AI response caching.
-   Temporary matching jobs.

------------------------------------------------------------------------

# 25. Object Storage

Use:

-   AWS S3
-   Cloudflare R2
-   Supabase Storage

Store:

-   Crop photos.
-   Quality images.
-   User-uploaded documents.
-   Optional farm images.

Never store large images directly inside PostgreSQL.

------------------------------------------------------------------------

# 26. AI / ML Stack

## LLM

Possible choices:

-   OpenAI API.
-   Gemini API.
-   Claude API.
-   Local/open-weight model where appropriate.

The LLM is primarily responsible for:

-   Natural language understanding.
-   Farmer conversation.
-   Listing generation.
-   Explanation.
-   Tool calling.
-   Multilingual interaction.

It should **not be the source of truth for structured market data**.

------------------------------------------------------------------------

## Vision

Options:

-   Multimodal LLM.
-   YOLO for object/defect detection.
-   EfficientNet / MobileNet for crop classification.
-   Custom classifier later.

### Recommended hackathon approach

Start with a multimodal model.

Add a lightweight custom model only if time permits.

------------------------------------------------------------------------

## Speech

Potential stack:

``` text
Whisper
+
LLM
+
TTS
```

Use speech recognition for farmer input and text-to-speech for
responses.

------------------------------------------------------------------------

# 26A. LLM Provider Decision — Groq

## Is Groq the best API?

**Groq is an excellent choice for this hackathon, but it is not objectively the best provider for every FarmMesh AI task.**

Groq's main advantage is **very fast inference**. It also currently provides multimodal vision models and tool use. Its documentation lists `qwen/qwen3.6-27b` as a multimodal model with text/image processing, tool use and JSON mode. citeturn0search2turn0search5

Groq also supports tool/function calling, which fits the vendor copilot architecture where the LLM calls controlled backend functions such as `get_local_prices()` or `find_buyers()`. citeturn0search6

### Recommended decision

Use:

**Groq as the primary fast LLM provider for the MVP**, with a provider abstraction.

Use the model/provider for:

- Vendor AI copilot.
- Listing generation.
- Structured intent extraction.
- Marketplace explanations.
- Multilingual text generation.
- Image understanding where the selected Groq multimodal model is suitable.

Do **not** use the LLM as the source of truth for:

- Current prices.
- Inventory.
- Buyer availability.
- Order status.
- Farmer earnings.
- Forecast values.
- Logistics capacity.

Those must come from backend data/services.

### Why not use Groq for everything?

FarmMesh has several different AI problems:

| Task | Best architecture |
|---|---|
| Chat / copilot | LLM |
| Listing generation | LLM |
| Image understanding | Multimodal model |
| Price prediction | Statistical/ML model + market data |
| Demand forecasting | Time-series/ML |
| Buyer matching | Deterministic scoring/learning-to-rank |
| Route optimization | OR-Tools |
| Market imbalance | Forecast + rules/ML |
| Scenario simulation | Deterministic simulation |
| Intervention optimization | OR-Tools / optimization |
| Explanation | LLM |

Therefore, **"Groq = the AI" is the wrong architecture**.

The correct architecture is:

```text
                         VENDOR
                            │
                            ▼
                     AI ORCHESTRATOR
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
           GROQ          ML SERVICES    OPTIMIZERS
             │              │              │
       Copilot / text   Forecasting      OR-Tools
       vision / tools   pricing/demand   routing/allocation
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                     VERIFIED JSON DATA
                            │
                            ▼
                       LLM EXPLANATION
```

### Groq structured output note

Groq supports Structured Outputs with JSON Schema. Its current documentation states that strict structured output is available for selected models, but strict Structured Outputs currently does not support tool use simultaneously. citeturn0search0

Therefore, do not design one giant Groq call that simultaneously requires strict schema enforcement and tool execution.

Instead use a controlled sequence:

```text
User request
   ↓
LLM intent/tool decision
   ↓
Backend tool executes
   ↓
Verified structured result
   ↓
LLM explains result
```

### Alternative: Gemini

Gemini is a strong alternative, particularly when image/multimodal capability and a generous developer free tier matter. Google's current developer documentation lists free access for selected models and free input/output tokens within applicable limits. citeturn0search3

For this project:

**Hackathon default:** Groq  
**Strong multimodal/free-tier alternative:** Gemini  
**Architecture rule:** keep the provider replaceable.

# 27. AI Service Design

Create an independent AI service:

``` text
/services/ai
    /vision
    /pricing
    /demand
    /recommendation
    /matching
    /copilot
```

Each model should expose a structured API.

### Example

``` http
POST /ai/analyze-harvest
```

Request:

``` json
{
  "image_url": "...",
  "quantity_kg": 30,
  "location": "Aluva"
}
```

Response:

``` json
{
  "crop": "green_chilli",
  "quality": "A",
  "confidence": 0.94,
  "recommended_price": {
    "min": 58,
    "max": 68
  }
}
```

------------------------------------------------------------------------

# 28. LLM Tool Calling

The farmer copilot should use tools.

Example tools:

``` text
get_farmer_inventory()
get_local_prices(crop, location)
find_buyers(crop, quantity, location)
estimate_net_revenue(listing_id)
create_listing(data)
accept_order(order_id)
get_demand_forecast(crop, location)
recommend_crops(farm_id)
```

### Example conversation

Farmer:

> "Who is buying my chilli?"

LLM:

``` text
find_buyers(
    crop="green_chilli",
    quantity=30,
    location="Aluva"
)
```

Backend returns actual buyers.

LLM then explains the result.

This prevents hallucinated marketplace information.

------------------------------------------------------------------------

## 28A. Revised Role and Onboarding Data Model

### User

```text
User
- id
- email
- email_verified
- name
- age / date_of_birth
- language
- role
- created_at
- updated_at
```

### VendorProfile

```text
VendorProfile
- id
- user_id
- farm_name
- farm_area
- location
- soil_type
- water_availability
- vendor_status
- created_at
```

### Role access matrix

| Capability | Standard User | Vendor | Admin |
|---|---:|---:|---:|
| Browse marketplace | Yes | Yes | Yes |
| Search products | Yes | Yes | Yes |
| Place orders | Yes | Yes | Yes |
| Create produce listings | No* | Yes | Yes |
| AI harvest analysis | No | Yes | Yes |
| AI price recommendation | No | Yes | Yes |
| Buyer matching tools | No | Yes | Yes |
| Market intelligence | No | Yes | Yes |
| Crop recommendation | No | Yes | Yes |
| Vendor AI copilot | No | Yes | Yes |
| Manage users | No | No | Yes |

*If the product later supports non-farmer sellers, replace this with a separate seller role rather than weakening the vendor definition.

# 29. Data Model

## User

``` text
User
- id
- name
- phone
- role
- language
- created_at
```

## Farmer

``` text
Farmer
- id
- user_id
- farm_area
- location
- soil_type
- water_availability
- reputation_score
```

## Farm

``` text
Farm
- id
- farmer_id
- latitude
- longitude
- area
- soil_data
```

## Crop

``` text
Crop
- id
- name
- category
- typical_harvest_days
```

## Listing

``` text
Listing
- id
- farmer_id
- crop_id
- quantity
- unit
- quality_grade
- price
- harvest_date
- image_url
- status
- location
```

## Buyer

``` text
Buyer
- id
- type
- location
- preferred_crops
- requirements
```

## Order

``` text
Order
- id
- buyer_id
- listing_ids
- quantity
- agreed_price
- logistics_cost
- farmer_payout
- status
```

## DemandSignal

``` text
DemandSignal
- id
- crop_id
- location
- date
- demand_score
- source
```

## Recommendation

``` text
Recommendation
- id
- farmer_id
- crop_id
- expected_profit
- risk_score
- confidence
- generated_at
```

------------------------------------------------------------------------

# 30. API Structure

``` text
/api/auth
/api/farmers
/api/farms
/api/crops
/api/listings
/api/buyers
/api/orders
/api/payments
/api/logistics
/api/ratings

/api/ai/analyze-harvest
/api/ai/generate-listing
/api/ai/price
/api/ai/match
/api/ai/demand
/api/ai/crop-recommendation
/api/ai/copilot
```

------------------------------------------------------------------------

# 31. Marketplace Matching Algorithm

## MVP algorithm

``` python
for listing in available_listings:

    compatible_buyers = find_buyers(
        crop=listing.crop,
        location=listing.location
    )

    for buyer in compatible_buyers:

        score = (
            crop_match(listing, buyer) * 0.30 +
            quantity_match(listing, buyer) * 0.20 +
            price_match(listing, buyer) * 0.15 +
            distance_score(listing, buyer) * 0.15 +
            quality_match(listing, buyer) * 0.10 +
            time_match(listing, buyer) * 0.10
        )

        rank(buyer, score)
```

Later, learn these weights from transaction outcomes.

------------------------------------------------------------------------

# 32. Crop Recommendation Algorithm

## Step 1 --- Generate candidate crops

Filter crops based on:

-   Climate.
-   Season.
-   Soil.
-   Water.
-   Farm area.

## Step 2 --- Calculate market potential

``` text
market_score =
    demand_forecast
    × expected_price
    × buyer_count
```

## Step 3 --- Calculate production economics

``` text
expected_profit =
    expected_revenue
    - seed_cost
    - fertilizer_cost
    - labor_cost
    - irrigation_cost
    - logistics_cost
```

## Step 4 --- Calculate risk

``` text
risk =
    price_volatility
    + disease_risk
    + demand_uncertainty
    + spoilage_risk
```

## Step 5 --- Rank

``` text
final_score =
    expected_profit
    × demand_probability
    × (1 - normalized_risk)
```

The UI should explain the ranking.

------------------------------------------------------------------------

# 33. Demand Forecasting Pipeline

``` text
Historical orders
       +
Search activity
       +
Buyer requirements
       +
Market prices
       +
Seasonality
       +
Weather
       +
Events
       ↓
Feature engineering
       ↓
Forecast model
       ↓
7/14/30 day demand
       ↓
Crop recommendation engine
```

------------------------------------------------------------------------

# 34. Logistics Optimization

For the MVP:

1.  Filter farmers within a pickup radius.
2.  Calculate distance.
3.  Group orders.
4.  Estimate vehicle capacity.
5.  Generate a route using OR-Tools.
6.  Calculate transport cost.
7.  Reject routes where logistics destroy farmer margin.

### Key metric

``` text
Net farmer payout per kg
```

not merely:

``` text
Gross selling price per kg
```

------------------------------------------------------------------------

# 35. Farmer App Screens

## Screen 1 --- Home

``` text
Good morning, Ravi

Today's harvest
35 kg

Potential earnings
₹2,150–₹2,450

AI opportunities
3 buyers looking for your crops
```

------------------------------------------------------------------------

## Screen 2 --- Sell

``` text
[ Take a photo ]

or

[ Speak ]

"I have 30 kilos of chilli."
```

------------------------------------------------------------------------

## Screen 3 --- AI Analysis

``` text
Green Chilli

Visual grade: A
Quantity: 30 kg

Suggested price
₹58–₹68/kg

3 nearby buyers
```

------------------------------------------------------------------------

## Screen 4 --- Matches

``` text
Restaurant A
Needs 20 kg
₹67/kg
2.8 km

Retailer B
Needs 100 kg
₹62/kg
6.4 km
```

------------------------------------------------------------------------

## Screen 5 --- Earnings

``` text
Today's sales

Gross       ₹2,010
Logistics   -₹180
Fees        -₹60
----------------
Net         ₹1,770
```

------------------------------------------------------------------------

## Screen 6 --- AI Farm Plan

``` text
Next 60 days

Recommended:
🌶️ Chilli     High opportunity
🥒 Cucumber   Medium
🍅 Tomato     Reduce

Reason:
Local tomato supply is currently high.
```

------------------------------------------------------------------------

# 36. Buyer Dashboard

## Dashboard

``` text
Procurement today

Tomato       120 / 150 kg
Green chilli  40 / 50 kg
Beans         65 / 70 kg
```

### Features

-   Search produce.
-   Create purchase requests.
-   View farmer profiles.
-   View quality information.
-   Request aggregated quantities.
-   Schedule recurring orders.
-   Track deliveries.
-   Rate suppliers.

------------------------------------------------------------------------

# 37. Admin Dashboard

Admin should see:

-   Total active farmers.
-   Active listings.
-   Active buyers.
-   Orders.
-   GMV.
-   Farmer payouts.
-   Average logistics cost.
-   Unsold inventory.
-   Demand forecasts.
-   AI recommendation accuracy.
-   Fraud/abuse alerts.

------------------------------------------------------------------------

# 38. Payments

For the hackathon MVP, payment can be simulated.

Production options may include:

-   Razorpay.
-   Cashfree.
-   UPI-compatible payment infrastructure.

### Payment flow

``` text
Buyer pays
    ↓
Platform records transaction
    ↓
Order completed
    ↓
Farmer payout calculated
    ↓
Settlement
```

Do not hold user funds in a custom wallet without understanding
applicable regulatory requirements.

------------------------------------------------------------------------

# 39. Notifications

Use:

-   Firebase Cloud Messaging.
-   SMS provider.
-   WhatsApp Business API where appropriate.

Notifications:

-   New buyer match.
-   Order accepted.
-   Pickup scheduled.
-   Delivery completed.
-   Payment status.
-   Demand opportunity.
-   Crop recommendation.

------------------------------------------------------------------------

# 40. Authentication

## MVP authentication

Use **email-based authentication**, matching the revised product vision.

Recommended flow:

```text
Email
  ↓
Sign up
  ↓
Email verification
  ↓
Session / access token
  ↓
Profile onboarding
  ↓
Role selection
```

### Required account fields

```text
User
- id
- email
- email_verified
- name
- age / date_of_birth (only if required)
- language
- role
- created_at
- updated_at
```

### Roles

```text
STANDARD_USER
VENDOR
ADMIN
```

### Security requirements

- Passwords must never be stored in plaintext.
- Prefer a managed authentication provider for the hackathon.
- Use secure HTTP-only cookies for web sessions where supported.
- If JWTs are used, keep access tokens short-lived and protect refresh tokens.
- Verify email ownership before activating the account.
- Rate-limit sign-in and verification attempts.
- Implement server-side role-based authorization.
- Never expose AI/vendor endpoints to standard users.
- Never put provider API keys in frontend code.

### Recommended auth implementation

For a web-first hackathon, use **Supabase Auth** or an equivalent managed email-auth provider rather than building password reset, verification, session rotation and abuse prevention from scratch.

------------------------------------------------------------------------

# 41. Security Requirements

## Backend

-   Validate every API request.
-   Use Pydantic schemas.
-   Parameterized database queries.
-   Authentication middleware.
-   Role-based authorization.
-   Rate limiting.
-   Secure file uploads.
-   Virus/malware scanning where applicable.
-   Encrypt sensitive data.
-   Do not expose object-storage credentials.

## AI security

Protect against:

-   Prompt injection.
-   Malicious uploaded content.
-   Data exfiltration.
-   Tool-call abuse.
-   Unauthorized marketplace actions.

### Important rule

The LLM must never have unrestricted database or payment access.

Use explicit tools with authorization checks.

------------------------------------------------------------------------

# 42. Privacy

Collect only necessary information.

Potentially sensitive data includes:

-   Phone number.
-   Farm location.
-   Financial transaction history.
-   Production information.

Do not expose precise farmer locations publicly.

Public listing should generally use:

> "Within 5 km of Aluva"

rather than exact coordinates.

------------------------------------------------------------------------

# 43. AI Hallucination Controls

Every AI output should have a source hierarchy.

### Ground truth

1.  Database.
2.  Verified market data.
3.  Model prediction.
4.  LLM explanation.

The LLM should never fabricate:

-   Buyers.
-   Prices.
-   Orders.
-   Farmer earnings.
-   Crop availability.

### Example

Bad:

> "Restaurant X will pay ₹80/kg."

Good:

> "Restaurant X currently has a purchase request for up to 50 kg at a
> maximum listed price of ₹80/kg."

------------------------------------------------------------------------

# 44. AI Confidence

Every recommendation should optionally include:

``` text
Confidence: High
```

or

``` text
Confidence: Medium
```

or

``` text
Confidence: Low
```

For low-confidence predictions:

> "Insufficient recent local data. Treat this estimate as indicative."

------------------------------------------------------------------------

# 45. Data Strategy

A hackathon will not have enough proprietary transaction data to train
sophisticated models.

Therefore use a **hybrid architecture**.

## Layer 1 --- Public data

Potential sources:

-   Government agricultural datasets.
-   Public market price datasets.
-   Weather APIs.
-   Public crop information.
-   Open agricultural research datasets.

## Layer 2 --- Synthetic data

Generate realistic transaction data for demonstration:

``` text
10,000 synthetic listings
5,000 buyer requests
20 crops
100 locations
180 days of price history
```

Clearly label synthetic data internally and never present it as real
transaction history.

## Layer 3 --- User-generated data

Once the product launches:

-   Listings.
-   Orders.
-   Search activity.
-   Buyer demand.
-   Prices.
-   Ratings.

This eventually becomes the platform's proprietary dataset.

------------------------------------------------------------------------

# 46. Recommended MVP AI Models

  -----------------------------------------------------------------------
  Problem                 MVP approach            Production approach
  ----------------------- ----------------------- -----------------------
  Crop identification     Multimodal LLM          Custom vision model

  Visual grading          Vision LLM + rules      Specialized classifier

  Listing generation      LLM                     LLM

  Translation             LLM                     Dedicated translation
                                                  model/API

  Voice input             Whisper/API             Fine-tuned speech stack

  Price prediction        XGBoost/rules           Gradient
                                                  boosting/time-series
                                                  ensemble

  Demand forecast         Seasonal baseline       Time-series/ML model

  Buyer matching          Weighted scoring        Learning-to-rank

  Crop recommendation     Optimization + ML       Personalized
                                                  recommendation model

  Logistics               OR-Tools                OR-Tools + learned
                                                  ETA/cost model

  Copilot                 LLM + tools             Agent + deterministic
                                                  services
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 47. Recommended Development Stack

``` text
Frontend
├── Flutter
├── Dart
└── Riverpod

Web
├── Next.js
├── TypeScript
└── Tailwind CSS

Backend
├── Python
├── FastAPI
├── Pydantic
└── SQLAlchemy

Database
├── PostgreSQL
├── PostGIS
└── Redis

AI
├── OpenAI / equivalent multimodal LLM
├── Whisper / speech API
├── scikit-learn
├── XGBoost
└── OR-Tools

Storage
└── S3-compatible object storage

Infrastructure
├── Docker
├── GitHub Actions
└── Cloud deployment

Maps
├── Google Maps or Mapbox
└── Geocoding + routing

Notifications
└── Firebase Cloud Messaging
```

------------------------------------------------------------------------

# 48. Repository Structure

``` text
farmmesh/
│
├── apps/
│   ├── farmer-mobile/
│   ├── buyer-web/
│   └── admin-web/
│
├── services/
│   ├── api/
│   │   ├── auth/
│   │   ├── farmers/
│   │   ├── listings/
│   │   ├── buyers/
│   │   ├── orders/
│   │   └── logistics/
│   │
│   └── ai/
│       ├── vision/
│       ├── pricing/
│       ├── demand/
│       ├── matching/
│       ├── recommendations/
│       └── copilot/
│
├── packages/
│   ├── schemas/
│   └── shared/
│
├── data/
│   ├── seed/
│   ├── synthetic/
│   └── reference/
│
├── infrastructure/
│   ├── docker/
│   └── deployment/
│
├── docs/
│   ├── architecture.md
│   ├── api.md
│   └── ai.md
│
├── .env.example
├── docker-compose.yml
└── README.md
```

------------------------------------------------------------------------

# 49. Environment Variables

``` env
DATABASE_URL=
REDIS_URL=

OPENAI_API_KEY=
GOOGLE_MAPS_API_KEY=
MAPBOX_TOKEN=

S3_ENDPOINT=
S3_ACCESS_KEY=
S3_SECRET_KEY=
S3_BUCKET=

FIREBASE_PROJECT_ID=
FIREBASE_CLIENT_EMAIL=
FIREBASE_PRIVATE_KEY=

JWT_SECRET=
```

Never commit `.env` files or production secrets to Git.

------------------------------------------------------------------------

# 50. MVP User Journey

## Shared onboarding

```text
Landing Page
    ↓
Sign up with email
    ↓
Verify email
    ↓
Name + age/profile details
    ↓
Are you a farmer/vendor?
    ├── No
    │    ↓
    │  Standard Marketplace
    │
    └── Yes
         ↓
       Vendor Profile
         ↓
       AI Vendor Workspace
```

## Standard user

```text
Sign up
  ↓
Profile
  ↓
Standard marketplace
  ↓
Search / browse
  ↓
Product details
  ↓
Cart / order
  ↓
Order tracking
```

## Vendor

```text
Sign up
  ↓
Profile
  ↓
Select farmer/vendor
  ↓
Create vendor profile
  ↓
Vendor dashboard
  ↓
Create harvest listing
  ↓
AI crop / quality analysis
  ↓
AI description
  ↓
AI price guidance
  ↓
Listing goes live
  ↓
AI buyer matching
  ↓
Supply aggregation
  ↓
Logistics estimate
  ↓
Order
  ↓
Vendor earnings
  ↓
Market intelligence
  ↓
Next-cycle recommendation
```

## Core UX principle

The standard user should never feel like they are using an agricultural AI system.

They are simply using a marketplace.

The vendor should feel that FarmMesh becomes an **AI operating layer around their marketplace activity**.

------------------------------------------------------------------------

# 51. Hackathon Demo Flow

The demo should tell one coherent story.

## Scenario

A small farmer has:

``` text
30 kg green chilli
20 kg tomato
25 kg beans
```

### Step 1

Farmer takes a picture.

AI identifies:

> Green chilli --- Grade A

### Step 2

Farmer speaks:

> "I have 30 kilos harvested today."

System creates listing.

### Step 3

AI shows:

> Recommended price: ₹60--₹68/kg

### Step 4

System finds:

``` text
Restaurant A → 15 kg
Retailer B → 50 kg
Consumer group → 20 kg
```

### Step 5

The system discovers another nearby farmer with:

``` text
25 kg chilli
```

It combines them:

``` text
30 kg + 25 kg = 55 kg
```

### Step 6

AI selects the most profitable allocation.

### Step 7

AI generates pickup route.

### Step 8

Dashboard shows:

``` text
Gross revenue       ₹3,520
Transport            -₹220
Platform costs       -₹90
---------------------------
Farmer net           ₹3,210
```

### Step 9

AI says:

> "Based on upcoming demand, consider increasing chilli allocation by
> 15% for the next cycle."

This demonstrates the entire platform.

------------------------------------------------------------------------

# 52. Success Metrics

## Marketplace

-   Number of active farmers.
-   Number of active buyers.
-   Listings created.
-   Orders completed.
-   Gross merchandise value.
-   Order fulfillment rate.
-   Repeat order rate.

## Farmer economics

### Primary metric

**Average farmer net realization**

Compare:

``` text
Traditional channel
vs.
FarmMesh
```

### Other metrics

-   Average selling price.
-   Logistics cost.
-   Time to sale.
-   Unsold produce.
-   Repeat buyer rate.

------------------------------------------------------------------------

# 53. AI Metrics

## Vision

-   Crop classification accuracy.
-   Quality classification accuracy.
-   Human correction rate.

## Pricing

-   Mean absolute error.
-   Percentage within actual transaction range.

## Demand

-   Forecast error.
-   Directional accuracy.

## Matching

-   Match acceptance rate.
-   Completed transaction rate.

## Recommendations

-   Recommendation acceptance.
-   Crop profitability.
-   Sale probability.

------------------------------------------------------------------------

# 54. Business Model

Potential models:

## Transaction fee

Take a small percentage of completed transactions.

Example:

``` text
₹1,000 transaction
↓
Platform fee
↓
Farmer receives remainder
```

The exact fee should be tested rather than assumed.

## Buyer subscription

Restaurants and retailers pay for:

-   Procurement tools.
-   Recurring orders.
-   Analytics.
-   Priority sourcing.

## Logistics margin

Charge for managed pickup/delivery where economically viable.

## Premium AI tools

Later:

-   Advanced crop planning.
-   Farm analytics.
-   Production forecasting.

------------------------------------------------------------------------

# 55. Unit Economics

This must be monitored from day one.

### Formula

``` text
Contribution Margin
=
Platform Revenue
− Payment Fees
− Logistics Subsidy
− Support Cost
− AI Inference Cost
− Other Variable Costs
```

For each order:

``` text
GMV
Farmer payout
Logistics cost
Platform fee
AI cost
Net contribution
```

A marketplace that increases farmer selling prices while losing money on
every delivery is not a sustainable business.

------------------------------------------------------------------------

# 56. Monetization Risk

Do not make farmers pay upfront in the MVP.

A transaction-based model is easier to test:

``` text
Successful sale
      ↓
Small platform fee
```

This aligns platform revenue with farmer success.

------------------------------------------------------------------------

# 57. Deployment

## Hackathon

Use:

``` text
Frontend → Vercel / equivalent
Backend → Render / Railway / AWS
Database → Supabase / managed PostgreSQL
Storage → S3-compatible storage
AI → API provider
Maps → Google Maps / Mapbox
```

Dockerize backend services.

------------------------------------------------------------------------

# 58. Observability

Implement:

-   Structured logs.
-   API latency monitoring.
-   AI request logging.
-   Error tracking.
-   Model confidence tracking.

Never log:

-   Passwords.
-   OTPs.
-   API keys.
-   Payment secrets.
-   Sensitive personal information.

------------------------------------------------------------------------

# 59. Testing

## Backend

-   Unit tests.
-   API integration tests.
-   Authentication tests.
-   Authorization tests.

## AI

Create a benchmark dataset:

``` text
100 crop images
100 price prediction cases
100 matching cases
50 crop recommendation cases
```

Measure model performance before the demo.

## Frontend

Test:

-   Slow network.
-   Failed upload.
-   Camera permission denied.
-   AI timeout.
-   Duplicate order.
-   Payment failure.

------------------------------------------------------------------------

# 60. Failure States

The product must work when AI fails.

### Vision failure

``` text
"We couldn't confidently identify this crop."

[Choose manually]
```

### Price model failure

``` text
"Not enough local data."

Show available market reference instead.
```

### Buyer matching failure

``` text
"No nearby buyers currently match."

[Create public listing]
```

### Logistics failure

``` text
"Delivery cost is currently too high."

[Try pickup]
[Wait for aggregation]
```

------------------------------------------------------------------------

# 61. Accessibility

Support:

-   Large buttons.
-   Minimal text.
-   Voice input.
-   Local languages.
-   Audio responses.
-   High-contrast UI.
-   Simple navigation.
-   Offline draft creation where possible.

------------------------------------------------------------------------

# 62. Offline Considerations

Farm connectivity may be unreliable.

MVP:

-   Cache farm profile.
-   Allow listing drafts offline.
-   Upload when connection returns.
-   Queue image uploads.
-   Avoid making the entire workflow dependent on continuous
    connectivity.

------------------------------------------------------------------------

# 63. Future Features

## Phase 2

-   More languages.
-   More crops.
-   Better demand prediction.
-   Buyer subscriptions.
-   Automated recurring procurement.
-   Digital invoices.
-   Better logistics optimization.

## Phase 3

-   IoT integration.
-   Soil sensors.
-   Satellite imagery.
-   Crop disease prediction.
-   Yield prediction.
-   Credit scoring based on transaction history, subject to regulation
    and responsible-use controls.

## Phase 4

-   Regional farmer cooperatives/FPO integration.
-   Institutional buyers.
-   Food processors.
-   Export workflows.
-   Cross-region supply optimization.

------------------------------------------------------------------------

# 64. What NOT to Build for the Hackathon

Avoid spending the majority of development time on:

-   Blockchain.
-   Complex payment wallets.
-   Custom drone systems.
-   Custom LLM training.
-   Nationwide logistics.
-   Hundreds of crop classes.
-   Full accounting.
-   Social media feeds.
-   Gamification.
-   A massive consumer grocery app.

The winning demo should show **intelligent coordination**, not feature
count.

------------------------------------------------------------------------

# 65. Recommended Hackathon Scope

## Must have

### Farmer

-   Authentication.
-   Farm profile.
-   Photo/voice harvest listing.
-   AI crop identification.
-   AI listing generation.
-   AI price recommendation.
-   Buyer matching.
-   Earnings view.

### Buyer

-   Buyer profile.
-   Purchase requirement.
-   Marketplace.
-   Order creation.

### AI

-   Vision.
-   LLM copilot.
-   Price engine.
-   Matching engine.
-   Basic demand recommendation.

### Logistics

-   Nearby farmer aggregation.
-   Basic route optimization.
-   Net revenue calculation.

------------------------------------------------------------------------

## Nice to have

-   Multilingual voice.
-   Demand forecasting.
-   Crop recommendations.
-   Recurring orders.
-   Reputation system.
-   Admin dashboard.

------------------------------------------------------------------------

# 66. 48-Hour Build Plan

## Hours 0--4

### Product

-   Finalize user journey.
-   Define schemas.
-   Create repository.
-   Set up database.
-   Set up authentication.

------------------------------------------------------------------------

## Hours 4--12

### Marketplace

Build:

-   Farmer profile.
-   Create listing.
-   Buyer profile.
-   Buyer requirements.
-   Listing feed.
-   Basic order flow.

------------------------------------------------------------------------

## Hours 12--20

### AI

Implement:

-   Crop identification.
-   Listing generation.
-   Price recommendation.
-   AI copilot.

------------------------------------------------------------------------

## Hours 20--28

### Matching

Implement:

-   Geographic filtering.
-   Buyer matching.
-   Supply aggregation.
-   Net revenue calculation.

------------------------------------------------------------------------

## Hours 28--36

### Logistics

Implement:

-   Pickup grouping.
-   Route calculation.
-   Estimated transport cost.

------------------------------------------------------------------------

## Hours 36--42

### UI polish

Focus on:

-   Farmer dashboard.
-   AI interaction.
-   Buyer dashboard.
-   Earnings visualization.

------------------------------------------------------------------------

## Hours 42--46

### Testing

Test the exact demo scenario repeatedly.

------------------------------------------------------------------------

## Hours 46--48

### Presentation

Prepare:

-   Problem.
-   Solution.
-   AI architecture.
-   Live demo.
-   Economics.
-   Future roadmap.

------------------------------------------------------------------------

# 67. Team Roles

## AI/ML Engineer

Own:

-   Vision.
-   Pricing.
-   Demand prediction.
-   Crop recommendation.
-   LLM tools.

## Backend Engineer

Own:

-   APIs.
-   Database.
-   Authentication.
-   Marketplace.
-   Orders.

## Frontend Engineer

Own:

-   Farmer app.
-   Buyer dashboard.
-   UX.
-   Localization.

## Optimization / Data Engineer

Own:

-   Matching.
-   Aggregation.
-   Logistics.
-   Data pipelines.

## Product / Presentation

Own:

-   Demo.
-   User journey.
-   Metrics.
-   Pitch.
-   Visual design.

For a smaller team, combine backend + data and frontend + product.

------------------------------------------------------------------------

# 68. Key Differentiator

FarmMesh should not be positioned as:

> **"An app where farmers sell vegetables."**

There are already many marketplaces and agricultural digital platforms.

Position it as:

> ## **AI Commerce Infrastructure for Small Farmers**

The system connects:

``` text
WHAT TO GROW
      ↓
HOW MUCH TO GROW
      ↓
WHEN TO HARVEST
      ↓
HOW TO PRICE
      ↓
WHO TO SELL TO
      ↓
HOW TO AGGREGATE
      ↓
HOW TO DELIVER
      ↓
HOW MUCH THE FARMER ACTUALLY EARNS
```

This creates a closed-loop system.

------------------------------------------------------------------------

# 69. The AI Flywheel

The long-term moat is data.

``` text
More farmers
      ↓
More supply data
      ↓
More listings
      ↓
More transactions
      ↓
More buyer demand data
      ↓
Better price predictions
      ↓
Better buyer matching
      ↓
Better crop recommendations
      ↓
More successful sales
      ↓
More farmers
```

The most valuable asset eventually becomes **localized agricultural
supply-and-demand intelligence**.

------------------------------------------------------------------------

# 70. Competitive Positioning

The platform should complement rather than simply attack:

-   Agricultural markets.
-   FPOs.
-   Existing marketplaces.
-   Local wholesalers.
-   Collection centers.

A useful positioning is:

> **FarmMesh is the intelligence and coordination layer that helps
> fragmented producers participate more effectively in existing
> agricultural commerce.**

------------------------------------------------------------------------

# 71. Risks & Mitigations

## Risk: AI gives incorrect crop identification

**Mitigation:** confidence threshold + manual correction.

## Risk: Incorrect price prediction

**Mitigation:** show ranges + confidence + source/reference data.

## Risk: Quality disputes

**Mitigation:** visual AI is advisory; buyer/aggregator confirmation
remains authoritative.

## Risk: Logistics destroys margin

**Mitigation:** calculate net revenue before confirming an order.

## Risk: Farmer adoption is low

**Mitigation:** voice-first + simple UI + assisted onboarding.

## Risk: Marketplace liquidity

**Mitigation:** launch geographically narrow and recruit both supply and
demand in the same region.

## Risk: Fake listings

**Mitigation:** phone verification + reputation + transaction history +
optional verification.

## Risk: Perishability

**Mitigation:** freshness timestamps + prioritized matching + time-aware
routing.

## Risk: Regulatory complexity

**Mitigation:** start as a marketplace/coordination platform and obtain
legal review before handling regulated payments, credit, insurance, or
agricultural trading activities.

------------------------------------------------------------------------

# 72. Critical Product Risks

### 1. Chicken-and-egg marketplace problem

No buyers → farmers leave.

No farmers → buyers leave.

**Solution:** initially target one geography and a small number of
high-frequency crops and recruit both sides manually.

------------------------------------------------------------------------

### 2. Small order economics

A ₹300 vegetable order cannot support expensive delivery.

**Solution:** prioritize B2B orders and aggregation.

------------------------------------------------------------------------

### 3. AI overclaiming

Agriculture has high uncertainty.

**Solution:** show confidence, sources, ranges, and human verification.

------------------------------------------------------------------------

### 4. Data scarcity

Sophisticated ML requires historical transactions.

**Solution:** start with hybrid models and progressively learn from
platform transactions.

------------------------------------------------------------------------

# 73. Recommended Initial Geography

For a hackathon prototype, do **not** attempt all of India.

Use a single region.

Example:

> **Kochi / Ernakulam**

Then demonstrate:

``` text
Farmers
↓
Nearby restaurants
↓
Local retailers
↓
Collection point
↓
Buyer
```

This makes the logistics story believable.

------------------------------------------------------------------------

# 74. Initial Crop Scope

Start with approximately:

-   Tomato.
-   Green chilli.
-   Beans.
-   Cucumber.
-   Banana.
-   Spinach/leafy vegetables.

Choose crops with:

-   Frequent demand.
-   Short shelf life.
-   Local production.
-   Easy visual identification.
-   Relatively straightforward marketplace transactions.

------------------------------------------------------------------------

# 75. Product North Star

### North Star Metric

> **Farmer net income generated through successful marketplace
> transactions.**

Supporting metrics:

``` text
Successful transactions
Farmer net realization
Time to sale
Buyer repeat rate
Supply aggregation rate
Logistics cost/kg
AI recommendation acceptance
```

------------------------------------------------------------------------

# 76. One-Sentence Pitch

> **FarmMesh is an AI-powered commerce platform that lets small farmers
> sell fragmented harvests directly to nearby buyers while using demand
> forecasting, intelligent pricing, supply aggregation, and logistics
> optimization to maximize their net income.**

------------------------------------------------------------------------

# 77. 30-Second Pitch

> Small farmers can grow valuable produce but often struggle to sell
> small quantities profitably. FarmMesh turns every small farm into a
> digital storefront. A farmer simply photographs or speaks about their
> harvest, and AI identifies the crop, estimates quality, recommends a
> price, finds nearby buyers, combines supply from other small farms
> when needed, and optimizes pickup. The same AI then learns local
> demand and recommends what the farmer should grow next. Instead of
> simply creating another agricultural marketplace, we're building an AI
> commerce layer for India's fragmented small-farm economy.

------------------------------------------------------------------------

# 77A. Vendor AI Market Intelligence Engine

The pasted AMIE specification is incorporated here as a **vendor-only intelligence module**, not as a separate product.

Its purpose is to answer:

> **"What is likely to happen to my market during my harvest window, why, and what can I do before the problem occurs?"**

The source architecture uses:

```text
Historical + current evidence
        ↓
State estimation
        ↓
Future-state forecasting
        ↓
Imbalance detection
        ↓
Hidden bottleneck discovery
        ↓
Counterfactual simulation
        ↓
Intervention optimization
        ↓
Action
```

This chain is taken from the supplied AMIE specification. fileciteturn0file1L29-L43

## Vendor-facing intelligence

### 1. Market outlook

Show:

- Expected local supply.
- Expected demand.
- Price direction.
- Surplus/shortage risk.
- Confidence.
- Data freshness.

### 2. Early imbalance detection

```text
forecast_supply - forecast_demand
```

Classify:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

The AMIE source recommends an imbalance ratio based on forecast supply versus forecast demand and configurable risk weights. fileciteturn0file1L847-L898

### 3. Bottleneck discovery

Do not assume that the most utilized node is automatically the bottleneck.

Consider:

- Utilization.
- Concentration.
- Lack of alternative capacity.
- Downstream impact.

This follows the supplied AMIE bottleneck approach. fileciteturn0file1L908-L999

### 4. What-if simulation

Vendor can test scenarios such as:

```text
Harvest +20%
Demand -15%
Transport +25%
Processor failure
Storage -30%
```

The system compares:

```text
DO NOTHING
vs
INTERVENTION
```

### 5. Recommended intervention

Potential recommendations:

- Redirect supply.
- Switch buyer/processor.
- Use alternative storage.
- Aggregate with nearby vendors.
- Change harvest allocation.
- Increase procurement.
- Reduce overloaded routes.

### 6. Vendor-facing output

Example:

```text
MARKET OUTLOOK — GREEN CHILLI

Expected supply:      1,180 kg/day
Expected demand:        940 kg/day

Surplus risk: HIGH
Confidence: MEDIUM

Why?
• Several nearby farms are expected to harvest simultaneously.
• Buyer demand is currently stable.
• Local processing capacity is near its projected limit.

Recommended action:
• Secure buyer commitments before harvest.
• Aggregate supply with nearby vendors.
• Consider allocating 20% to Buyer B.

Data status:
Market data updated 6 hours ago.
```

### Important architecture rule

The LLM only explains structured results.

```text
Market data
    ↓
Forecast engine
    ↓
Risk engine
    ↓
Simulation / optimizer
    ↓
Verified JSON
    ↓
Groq / other LLM
    ↓
Human-readable explanation
```

The supplied AMIE specification explicitly states that the LLM is optional and must not invent forecasts, capacities, bottlenecks or optimization results. fileciteturn1file1L874-L901

## MVP scope for AMIE

Do not implement the full research system initially.

### MVP

- Market data ingestion.
- Simple supply/demand forecast.
- Imbalance score.
- Basic bottleneck score.
- One or two what-if scenarios.
- One intervention recommendation.
- Vendor-facing explanation.

### Later

- Better time-series models.
- Infrastructure network modeling.
- More shocks.
- Counterfactual simulation.
- OR-Tools optimization.
- Experiment comparison between public-only data and public + farmer + buyer state.

The AMIE specification itself recommends simple forecasting baselines before complex models and validates time-series models chronologically. fileciteturn0file1L737-L841

------------------------------------------------------------------------

# 78. Final Architecture

```text
                         ┌─────────────────────────┐
                         │       NEXT.JS WEB       │
                         │ Landing / Auth / Shop   │
                         └────────────┬────────────┘
                                      │
                               Email Auth
                                      │
                         ┌────────────▼────────────┐
                         │      FASTAPI BACKEND    │
                         │ Auth / RBAC / Marketplace│
                         └────────────┬────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
              Standard User        Vendor           Admin
                    │                 │
                    ▼                 ▼
             Marketplace       Vendor Workspace
                                      │
                    ┌─────────────────┼──────────────────┐
                    │                 │                  │
                    ▼                 ▼                  ▼
               Harvest AI      Market Intelligence   Farm Planning
                    │                 │                  │
                    ▼                 ▼                  ▼
               Vision/LLM       Forecast/Risk       Crop Ranking
                    │                 │                  │
                    └─────────────────┼──────────────────┘
                                      │
                              AI ORCHESTRATOR
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
                  Groq            ML Models         OR-Tools
              LLM / Vision      Price / Demand     Routing / Opt.
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      ▼
                            PostgreSQL + PostGIS
                                      │
                         ┌────────────┴────────────┐
                         ▼                         ▼
                    Redis / Jobs              Object Storage
```

The key architectural boundary is:

> **Marketplace functionality is available to standard users; AI vendor services are protected by server-side vendor authorization.**

# 79. Final MVP Definition

The MVP is complete when a judge can perform both sides of the product without developer intervention.

### Standard user path

```text
1. Register with email
2. Verify email
3. Complete profile
4. Select "Not a farmer/vendor"
5. Enter normal marketplace
6. Browse/search products
7. View listing
8. Place an order
9. View order status
```

### Vendor path

```text
1. Register with email
2. Verify email
3. Complete profile
4. Select "Farmer/vendor"
5. Create vendor/farm profile
6. Enter vendor workspace
7. Upload crop photo
8. AI identifies crop
9. Enter/speak quantity
10. AI generates listing
11. AI recommends a price range
12. Listing appears in marketplace
13. AI matches buyers
14. System aggregates supply where useful
15. System calculates logistics/net earnings
16. Buyer confirms order
17. Vendor sees earnings
18. Vendor sees market outlook
19. Vendor receives next-cycle recommendation
```

If both flows work reliably, the project demonstrates the revised FarmMesh thesis.

------------------------------------------------------------------------

# 80. Final Product Thesis

FarmMesh should ultimately behave less like a conventional marketplace
and more like an **AI operating system for small agricultural
commerce**.

The platform should continuously answer five questions:

> **What do I have?**

> **What is it worth?**

> **Who wants it?**

> **How do I get it there profitably?**

> **What should I grow next?**

That closed loop is the core product.

------------------------------------------------------------------------

## Appendix A --- Recommended MVP Priority

  Priority   Feature                   Importance
  ---------- ------------------------- -------------
  P0         Farmer onboarding         Critical
  P0         Harvest listing           Critical
  P0         AI crop identification    Critical
  P0         AI price recommendation   Critical
  P0         Buyer marketplace         Critical
  P0         Buyer matching            Critical
  P0         Order flow                Critical
  P0         Farmer earnings           Critical
  P1         Supply aggregation        Very high
  P1         Logistics optimization    Very high
  P1         AI copilot                Very high
  P1         Demand forecasting        High
  P1         Crop recommendation       High
  P1         Voice interface           High
  P2         Reputation                Medium
  P2         Recurring orders          Medium
  P2         Advanced forecasting      Medium
  P2         IoT integration           Low for MVP

------------------------------------------------------------------------

## Appendix B --- Recommended First Prototype

If development time becomes constrained, reduce the product to:

### Farmer

``` text
Photo → AI crop detection → quantity → price → listing
```

### Buyer

``` text
Requirement → matching → order
```

### AI

``` text
Vision
+
Price estimation
+
Matching
+
Simple crop recommendation
```

### Logistics

``` text
Nearby farmers → aggregate → route → net earnings
```

This is the smallest version that still communicates the full product
thesis.

------------------------------------------------------------------------

## Appendix C0 --- Revised MVP Priority

| Priority | Feature | User |
|---|---|---|
| P0 | Email authentication | Everyone |
| P0 | Profile onboarding | Everyone |
| P0 | Farmer/vendor role selection | Everyone |
| P0 | Standard marketplace | Everyone |
| P0 | Vendor profile | Vendor |
| P0 | Produce listing | Vendor |
| P0 | AI listing generation | Vendor |
| P0 | AI price guidance | Vendor |
| P0 | Basic buyer matching | Vendor |
| P0 | Basic order flow | Everyone |
| P1 | AI crop/image analysis | Vendor |
| P1 | AI copilot | Vendor |
| P1 | Market outlook | Vendor |
| P1 | Supply/demand imbalance | Vendor |
| P1 | Supply aggregation | Vendor |
| P1 | Logistics estimate | Vendor |
| P1 | Crop recommendation | Vendor |
| P2 | Full bottleneck simulation | Vendor |
| P2 | Advanced forecasting | Vendor |
| P2 | Recurring procurement | Vendor/Buyer |
| P2 | Mobile app | Everyone |

### Important scope decision

Do **not** build a separate Flutter application for the first web MVP.

Build one responsive Next.js website. If adoption later justifies a native app, the backend APIs can support Flutter/React Native without changing the core marketplace and AI services.

------------------------------------------------------------------------

## Appendix C --- Definition of Done

### Product

-   [ ] Farmer can register.
-   [ ] Farmer can create a farm.
-   [ ] Farmer can create a listing.
-   [ ] Buyer can create a requirement.
-   [ ] Buyer can place an order.
-   [ ] Farmer can view earnings.

### AI

-   [ ] Crop can be identified from an image.
-   [ ] Listing description can be generated.
-   [ ] Price range can be calculated.
-   [ ] Buyers can be ranked.
-   [ ] Multiple farmers can be aggregated.
-   [ ] Crop recommendation can be generated.
-   [ ] AI outputs include uncertainty where appropriate.

### Infrastructure

-   [ ] PostgreSQL configured.
-   [ ] Object storage configured.
-   [ ] API authentication implemented.
-   [ ] Environment secrets protected.
-   [ ] Error handling implemented.
-   [ ] Basic logging implemented.

### Demo

-   [ ] Complete farmer-to-buyer flow works.
-   [ ] AI response time is acceptable.
-   [ ] Demo data is seeded.
-   [ ] Logistics calculation works.
-   [ ] Farmer net earnings are visible.
-   [ ] Presentation explains the AI architecture.
## Appendix D --- Verified MVP Dependency Set

### Required

```text
Frontend
- Next.js
- TypeScript
- Tailwind CSS
- React Hook Form
- Zod
- TanStack Query

Backend
- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic

Database
- PostgreSQL
- PostGIS

Authentication
- Supabase Auth or equivalent managed email authentication

AI
- Groq API
- Provider abstraction for Gemini/fallback
- Multimodal model for image analysis

ML / Intelligence
- pandas
- NumPy
- scikit-learn
- XGBoost (only if useful)
- OR-Tools

Storage
- Supabase Storage or S3-compatible object storage
```

### Optional until needed

```text
- Redis
- Celery
- Mapbox / MapLibre
- Firebase Cloud Messaging
- Docker
- GitHub Actions
```

### Do not add without a concrete requirement

```text
- Flutter
- Kubernetes
- Microservice sprawl
- Custom LLM training
- Blockchain
- Vector database
- Complex event streaming
```

A hackathon architecture should minimize operational surface area. The original PRD already warns against unnecessary production-scale complexity and recommends a focused MVP. fileciteturn2file0L312-L328

