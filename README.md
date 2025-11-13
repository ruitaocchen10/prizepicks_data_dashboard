# PrizePicks EV Dashboard 

An analytics dashboard for monitoring positive expected value (EV) betting opportunities and user behavior patterns on PrizePicks. Built as a basic framework for a tool that could be used by PrizePicks data analysts to identify potentially vulnerable lines and advantageous users.

**Link to Project**: https://prizepicks-data-dashboard.vercel.app/

**Link to my Project Logs (hopefully it's entertaining)**: https://docs.google.com/document/d/1VKEOSDAL8rq9L22MP5xu_Gl5CDpOxDFhtuZFRKod2Vg/edit?tab=t.0

> **Note**: This project was created for educational purposes only. All data is either publicly available or simulated.
> **Also Note**: If you're using the link to view the project, I am using the Render free plan so the first load might take > 30 seconds... so just keep that in mind. I am broke sorry.

---

## Project Description

### The Problem
PrizePicks is playing the battle against sharp bettors in order to make money. Hobbyists are pretty much always going to lose money in the long run, but the sharp bettors who can monitor sportsbook lines and identify positive expected values in certain picks at certain times are the ones who can potentially profit from PrizePicks in the long run. In order to stay ahead of these betters, PrizePicks needs to: 

1. Monitor and limit the plus expected value opportunities that exist at every single moment during games, after games, before games - basically 24/7 (I know I used a dash there but I swear to God none of this was AI written I actually wrote it all and thought it out myself)
2. Monitor and limit users who are consistently taking advantage of plus expected value lines. Realistically, so many users are using tools out there to take advantage of the system, but since PrizePicks reserves the right to limit these users, they have to stay ahead as much as possible in order to make as much profit as possible
it their activity

### The Solution
This dashboard provides two core features that would help a platform like PrizePicks stay ahead:

**1. EV Monitoring Dashboard**
- Continuously tracks props from multiple sportsbooks
- Compares sportsbook odds with PrizePicks lines in real-time
- Calculates expected value for each betting opportunity
- Displays breakeven probabilities for different slip types (2-6 picks)
- Highlights the most +EV opportunities available

**2. User Analytics Dashboard**
- Monitors user betting patterns and profitability
- Identifies top-earning users (potential sharp bettors)
- Tracks most frequently exploited betting lines
- Provides SQL-based querying with natural language search
- Generates actionable insights for risk management

### Tech Stack

**Backend**
- **Python**: Data collection, processing, and API server
- **Flask**: RESTful API with CORS support
- **SQLite**: Relational database for user data
- **The Odds API**: Real-time sportsbook data
- **PrizePicks API**: Prop betting lines

**Frontend**
- **React**: UI component library
- **Next.js**: React framework with server-side rendering
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first styling
- **Custom CSS**: Polished, professional design

**Data Processing**
- **JSON**: Data storage and API responses
- **Subprocess**: Script orchestration
- **Request headers**: Bot protection bypass

---

## Main Struggles

### 1. **API Rate Limits & Credits**
**Problem**: Most sportsbook API charge a LOT of money.

**Solution**: 
- Limited data collection to passing yards only (less variation than other stats)
- Restricted to 5 games per refresh to stay within the 500 calls/month free tier
- Avoided unnecessary API calls by caching data locally

### 2. **PrizePicks Bot Protection**
**Problem**: PrizePicks has strong bot detection that blocks basic API requests with 403 errors.

**Solution**:
- Added comprehensive browser headers (User-Agent, Referer, Origin, Sec-Fetch-*)
- Implemented request delays to mimic human behavior
- Used educational/research justification for data access

### 3. **Data Matching Challenges**
**Problem**: PrizePicks and sportsbooks don't always have identical lines:
- PrizePicks: 235.5 passing yards
- Sportsbook: 237.5 passing yards

**Solution**:
- Implemented ±2.5 yard tolerance for matching
- Filtered out "Demon" and "Goblin" lines (I was so not aware of these before I did this project) to focus on standard lines only
- Created a fixed adjustment rate (probably not the most accurate but I really just wanted to get this to production)
- 
### 4. **Mock Data Generation**
**Problem**: Needed realistic user data without access to actual PrizePicks database.

**Solution**:
- Created SQLite schema with 7 tables
- Wrote seed script with configurable user distributions and win rates
- Used AI to help generate player names (despite some outdated team rosters - Javonte is NOT still on the Broncos)
- Accepted imperfect data since the goal was demonstrating the system

### 5. **CSS and UI Design**
**Problem**: AI-generated UI was dead ugly and difficult to customize.

**Struggles**:
- Claude struggled to implement specific UI changes correctly
- My CSS knowledge was more rusty than expected
- Spent hours manually debugging CSS issues

**Key Learning**: Having a clear design vision before coding saves massive amounts of time.

---

## Things I Learned

### Technical Skills

**1. API Integration & Management**
- How to work within API rate limits and optimize request patterns

**2. Database Design**
- Designing normalized relational schemas (SQLite)
- Writing efficient SQL queries for analytics

**3. Data Processing Pipelines**
- Building multi-stage data processing workflows
- Handling mismatched data from different sources
- Choosing the right data format (JSON vs SQL) for different use cases

**4. CSS & UI Development**
- Custom CSS for fine-grained control
- Figma for UI/UX design
- The gap between design mockups and implementation

### Soft Skills & Project Management

**1. Debugging Methodology**
- Breaking down complex problems into smaller pieces
- Using console logging strategically
- Reading error messages carefully
- Testing one component at a time

**2. Scope Management**
- Knowing when to cut features to meet deadlines
- Prioritizing MVP functionality over perfection
- Accepting "good enough" when appropriate (e.g., AI-generated player data)

**3. Documentation Habits**
- Keeping project logs to track progress and decisions
- Writing clear comments in code
- Using .env files and .gitignore for security

**4. Problem-Solving Creativity**
- Finding workarounds for API limitations (switching from TDs to yards)
- Accepting imperfect data when perfection isn't critical
- Knowing when to pivot strategies (JSON over SQL tables for initial processing)

## Next Steps

### What I Would Love to do Short-Term

**1. Expand Sports Coverage**
- Have a full dashboard of sports coverage with accurate ways to filter between them
- Be able to view +EV opportunities in NBA, UFC, soccer, MLB, etc.
- However, I'm not paying for more APIs so...

**2. Enhanced EV Calculations**
- Factor in correlation between picks on the same slip
- Account for variance and standard deviation

**3. Be able to account for goblin and demon lines**
- Man PrizePicks really out here finding more ways to limit positive value opportunities
- At least I'm assuming that's what this is

### Long-Term Features

**1. AI Agent Integration**
- Adding an AI Agent to extract VERY high-risk and VERY sharp bettors faster

## License

This project is for educational purposes only. All data is publicly available or simulated.

---

## Acknowledgments

- **The Odds API** for providing sports betting data
- **PrizePicks** for API availability (used for educational purposes)
- **Claude AI** for debugging assistance and code generation
- **Coffee shops** for providing the environment where most of this was built
