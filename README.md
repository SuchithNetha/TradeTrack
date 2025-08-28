# TradeTrack - Advanced Trading Journal Application

A comprehensive trading journal application designed to help traders track, analyze, and improve their trading performance through detailed analytics, AI-powered insights, and professional reporting.

## 🚀 Features

### Core Functionality
- **Trade Entry & Management**: Easy-to-use interface for recording trades with detailed metadata
- **Real-time Analytics**: Comprehensive performance metrics and risk analysis
- **AI-Powered Insights**: Intelligent analysis of trading patterns and recommendations
- **Professional Reports**: Downloadable PDF reports with charts and insights
- **User Authentication**: Secure user accounts with JWT authentication
- **Multi-Asset Support**: Track trades across various instruments (stocks, crypto, forex, etc.)

### Advanced Analytics
- **Performance Metrics**: Win rate, profit factor, Sharpe ratio, drawdown analysis
- **Risk Management**: Value at Risk (VaR), Expected Shortfall, Sortino ratio
- **Emotional Analysis**: Track emotional states and their impact on performance
- **Setup Analysis**: Evaluate effectiveness of different trading setups
- **Streak Analysis**: Monitor winning and losing streaks

### User Experience
- **Dashboard**: Real-time overview of trading performance
- **Filtering & Search**: Advanced filtering by asset, setup, emotion, date range
- **Charts & Visualizations**: Interactive charts for performance analysis
- **Mobile-Friendly**: Responsive design for all devices

## 📋 Requirements

- Python 3.8+
- FastAPI
- pandas, numpy, matplotlib
- reportlab (for PDF generation)
- python-jose (for JWT)
- passlib (for password hashing)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd trading_journal_project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

## 🎯 Quick Start

1. **Start the server**
   ```bash
   python run.py
   ```

2. **Access the API documentation**
   - Open your browser to `http://localhost:8000/docs`
   - Explore the interactive API documentation

3. **Create your first user**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/signup" \
        -H "Content-Type: application/json" \
        -d '{"username": "trader1", "password": "securepassword"}'
   ```

4. **Login and get token**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=trader1&password=securepassword"
   ```

5. **Add your first trade**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/trades/" \
        -H "Authorization: Bearer YOUR_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
          "date": "2024-01-15T10:30:00",
          "asset": "Bitcoin",
          "buy_price": 45000.0,
          "sell_price": 46000.0,
          "quantity": 1,
          "setup_type": "Breakout",
          "emotion": "Calm",
          "confidence_score": 8,
          "mistake": false,
          "notes": "Good breakout trade, followed the plan"
        }'
   ```

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/signup` - Create new user account
- `POST /api/v1/auth/login` - Login and get access token

### Trades Management
- `POST /api/v1/trades/` - Add new trade
- `GET /api/v1/trades/` - Get trades with filters
- `GET /api/v1/trades/{trade_id}` - Get specific trade
- `PUT /api/v1/trades/{trade_id}` - Update trade
- `DELETE /api/v1/trades/{trade_id}` - Delete trade

### Analytics
- `GET /api/v1/stats/` - Get trading statistics
- `GET /api/v1/trades/summary/performance` - Performance summary
- `GET /api/v1/trades/summary/equity-curve` - Equity curve data

### Dashboard
- `GET /api/v1/dashboard/` - Dashboard overview
- `GET /api/v1/dashboard/quick-stats` - Quick statistics
- `GET /api/v1/dashboard/performance-chart` - Chart data
- `GET /api/v1/dashboard/insights` - Trading insights

### AI Analysis
- `POST /api/v1/ai/explain` - Get AI-powered trade analysis

### Reports
- `GET /api/v1/report/download` - Download PDF report

## 📈 Data Models

### Trade Entry
```json
{
  "date": "2024-01-15T10:30:00",
  "asset": "Bitcoin",
  "buy_price": 45000.0,
  "sell_price": 46000.0,
  "quantity": 1,
  "setup_type": "Breakout",
  "emotion": "Calm",
  "confidence_score": 8,
  "mistake": false,
  "notes": "Trade notes and analysis",
  "stop_loss": 44000.0,
  "target": 47000.0,
  "holding_time": "2 hours",
  "market_condition": "Bullish",
  "news_impact": "Positive earnings"
}
```

### Supported Assets
- Bitcoin, BankNifty, Nasdaq, Nifty, Gold, Silver, Forex, Crypto, Stocks, Options, Futures

### Supported Setup Types
- Breakout, Reversal, News Play, Trend Following, Scalp, Swing, Positional, Intraday

### Supported Emotions
- Calm, Confident, Fearful, Greedy, Revenge, Excited, Anxious, Neutral

## 📊 Analytics Features

### Performance Metrics
- **Total Trades**: Number of completed trades
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Ratio of gross profit to gross loss
- **Average Win/Loss**: Average profit and loss per trade
- **Sharpe Ratio**: Risk-adjusted return measure
- **Maximum Drawdown**: Largest peak-to-trough decline

### Risk Metrics
- **Value at Risk (VaR)**: Potential loss at 95% confidence
- **Expected Shortfall**: Average loss beyond VaR
- **Sortino Ratio**: Downside risk-adjusted return
- **Calmar Ratio**: Return relative to maximum drawdown

### Behavioral Analysis
- **Emotional Impact**: Correlation between emotions and performance
- **Setup Effectiveness**: Performance by trading setup
- **Mistake Analysis**: Impact of trading mistakes
- **Streak Analysis**: Winning and losing streaks

## 🎨 Report Generation

The application generates comprehensive PDF reports including:

- **Executive Summary**: Key performance metrics
- **Performance Analysis**: Breakdown by asset, setup, and emotion
- **Risk Analysis**: Advanced risk metrics
- **Trading Insights**: AI-generated insights and recommendations
- **Charts & Visualizations**: Equity curve, performance charts
- **Best/Worst Trades**: Notable trade analysis

## 🔧 Configuration

### Environment Variables
```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/trading_journal

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=720

# Application Settings
DEBUG=True
ENVIRONMENT=development

# File Paths
DATA_DIR=./data
REPORTS_DIR=./reports
```

## 🚀 Deployment

### Development
```bash
python run.py
```

### Production
```bash
# Using Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Using Docker
docker build -t tradeinsight .
docker run -p 8000:8000 tradeinsight
```

## 📝 Usage Examples

### Python Client Example
```python
import requests

# Base URL
BASE_URL = "http://localhost:8000/api/v1"

# Login
response = requests.post(f"{BASE_URL}/auth/login", data={
    "username": "trader1",
    "password": "securepassword"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Add trade
trade_data = {
    "date": "2024-01-15T10:30:00",
    "asset": "Bitcoin",
    "buy_price": 45000.0,
    "sell_price": 46000.0,
    "quantity": 1,
    "setup_type": "Breakout",
    "emotion": "Calm",
    "confidence_score": 8,
    "mistake": False,
    "notes": "Good breakout trade"
}

response = requests.post(f"{BASE_URL}/trades/", json=trade_data, headers=headers)
print(response.json())

# Get dashboard
response = requests.get(f"{BASE_URL}/dashboard/", headers=headers)
print(response.json())
```

### JavaScript/Node.js Example
```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000/api/v1';

async function main() {
    // Login
    const loginResponse = await axios.post(`${BASE_URL}/auth/login`, {
        username: 'trader1',
        password: 'securepassword'
    });
    
    const token = loginResponse.data.access_token;
    const headers = { Authorization: `Bearer ${token}` };
    
    // Add trade
    const tradeData = {
        date: '2024-01-15T10:30:00',
        asset: 'Bitcoin',
        buy_price: 45000.0,
        sell_price: 46000.0,
        quantity: 1,
        setup_type: 'Breakout',
        emotion: 'Calm',
        confidence_score: 8,
        mistake: false,
        notes: 'Good breakout trade'
    };
    
    const tradeResponse = await axios.post(`${BASE_URL}/trades/`, tradeData, { headers });
    console.log(tradeResponse.data);
    
    // Get dashboard
    const dashboardResponse = await axios.get(`${BASE_URL}/dashboard/`, { headers });
    console.log(dashboardResponse.data);
}

main().catch(console.error);
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the examples in this README

## 🔮 Roadmap

- [ ] Real-time market data integration
- [ ] Advanced charting capabilities
- [ ] Mobile application
- [ ] Social features (trade sharing)
- [ ] Backtesting capabilities
- [ ] Portfolio management
- [ ] Multi-user collaboration
- [ ] Advanced AI insights
- [ ] Integration with brokers
- [ ] Automated trade logging

---

**TradeInsight** - Empowering traders with data-driven insights for better decision making.
