# 🚀 Client Delivery Guide

This guide explains how to deliver your ChatBot SaaS to clients, manage their accounts, and provide ongoing support.

## 📋 Pre-Delivery Checklist

### 1. Server Setup
- [ ] Deploy the application to a production server
- [ ] Configure SSL/HTTPS
- [ ] Set up proper domain name
- [ ] Configure environment variables
- [ ] Set up monitoring and logging
- [ ] Create database backups

### 2. Admin Access
- [ ] Change default admin API key
- [ ] Set up admin dashboard access
- [ ] Configure email notifications
- [ ] Set up usage monitoring

## 🎯 Client Onboarding Process

### Step 1: Create Client Account

**Option A: Using the Admin Dashboard**
1. Go to `https://your-domain.com/admin`
2. Use admin API key: `admin-secret-key-12345`
3. Fill in client information:
   - Company Name
   - Contact Email
   - Contact Name
   - Plan Type (Free/Basic/Pro/Enterprise)
4. Click "Create Client"

**Option B: Using the Onboarding Script**
```bash
python scripts/onboard_client.py
```

### Step 2: Generate API Key
1. In the admin dashboard, find the client
2. Click "Add API Key"
3. Enter a descriptive name (e.g., "Production", "Development")
4. Copy the generated API key

### Step 3: Create Integration Code
The system automatically generates integration code like this:

```html
<!-- ChatBot Widget Integration -->
<script src="https://your-domain.com/widget.js"></script>
<script>
  ChatBotWidget.init({
    clientId: 'client_abc12345',
    apiKey: 'cb_xyz789...',
    title: 'Chat with us',
    primaryColor: '#007bff',
    welcomeMessage: 'Hello! How can I help you today?'
  });
</script>
```

### Step 4: Send to Client
Send the client:
1. **Integration Code** - The HTML snippet above
2. **API Key** - For direct API access
3. **Client ID** - For reference
4. **Documentation** - This guide and API docs

## 📊 Available Plans

| Plan | Documents | Requests/Month | Price | Features |
|------|-----------|----------------|-------|----------|
| Free | 10 | 1,000 | $0 | Basic chatbot |
| Basic | 100 | 10,000 | $29/month | Standard features |
| Pro | 1,000 | 100,000 | $99/month | Advanced features |
| Enterprise | Unlimited | Unlimited | Custom | Full support |

## 🔧 Client Integration Options

### Option 1: Widget Integration (Recommended)
```html
<!-- Add to any website -->
<script src="https://your-domain.com/widget.js"></script>
<script>
  ChatBotWidget.init({
    clientId: 'CLIENT_ID',
    apiKey: 'API_KEY',
    title: 'Chat with us',
    primaryColor: '#007bff'
  });
</script>
```

### Option 2: Direct API Integration
```javascript
// For custom implementations
const response = await fetch('https://your-domain.com/ask', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer API_KEY'
  },
  body: JSON.stringify({
    client_id: 'CLIENT_ID',
    query: 'User question'
  })
});
```

### Option 3: Upload Documents
```bash
# Upload PDF documents
curl -X POST "https://your-domain.com/upload-pdf" \
  -H "Authorization: Bearer API_KEY" \
  -F "client_id=CLIENT_ID" \
  -F "doc_id=document-1" \
  -F "file=@document.pdf"
```

## 📈 Usage Monitoring

### Admin Dashboard Features
- **Real-time Stats**: Total clients, requests, documents
- **Client Management**: Create, update, suspend clients
- **API Key Management**: Generate, revoke, monitor keys
- **Usage Tracking**: Per-client usage statistics
- **Plan Management**: Upgrade/downgrade plans

### Usage Limits
- **Document Limits**: Maximum number of documents per plan
- **Request Limits**: Monthly API request limits
- **File Size Limits**: 10MB per PDF upload
- **Rate Limiting**: Automatic throttling for excessive usage

## 🛠️ Client Support

### Common Issues & Solutions

**1. Widget Not Appearing**
- Check if the script is loaded correctly
- Verify client ID and API key
- Check browser console for errors
- Ensure HTTPS is used in production

**2. API Key Errors**
- Verify API key is correct
- Check if key is expired
- Ensure proper Authorization header format
- Contact admin if key is revoked

**3. Usage Limit Exceeded**
- Check current usage in admin dashboard
- Upgrade plan if needed
- Wait for monthly reset
- Contact support for emergency increases

**4. Document Upload Issues**
- Check file size (max 10MB)
- Ensure file is PDF format
- Verify client has document quota remaining
- Check file is not corrupted

### Support Channels
- **Email**: support@your-domain.com
- **Admin Dashboard**: https://your-domain.com/admin
- **API Documentation**: https://your-domain.com/docs
- **Status Page**: https://status.your-domain.com

## 🔒 Security & Compliance

### Data Protection
- All data is isolated per client
- API keys are encrypted and secure
- No cross-client data access
- Automatic data retention policies

### Best Practices for Clients
1. **Keep API Keys Secure**: Don't expose in client-side code
2. **Use HTTPS**: Always use secure connections
3. **Monitor Usage**: Track API usage regularly
4. **Rotate Keys**: Periodically regenerate API keys
5. **Validate Input**: Sanitize user inputs before sending

## 📞 Client Communication Templates

### Welcome Email
```
Subject: Welcome to Your ChatBot - Setup Instructions

Hi [Client Name],

Welcome to [Your Company] ChatBot! Here's everything you need to get started:

🔑 Your Credentials:
- Client ID: [CLIENT_ID]
- API Key: [API_KEY]

📋 Integration Code:
[INTEGRATION_CODE]

📚 Documentation:
- Setup Guide: [LINK]
- API Documentation: [LINK]
- Admin Dashboard: [LINK]

🎯 Next Steps:
1. Add the integration code to your website
2. Upload your documents via the API
3. Test the chatbot functionality
4. Customize the appearance as needed

Need help? Contact us at support@your-domain.com

Best regards,
[Your Name]
[Your Company]
```

### Usage Alert Email
```
Subject: Usage Alert - [Client Name]

Hi [Client Name],

Your ChatBot usage is approaching the limit for your [PLAN] plan:

📊 Current Usage:
- Documents: X/Y
- Requests this month: X/Y

💡 Options:
1. Upgrade to a higher plan
2. Wait for monthly reset
3. Contact us for custom limits

To upgrade, visit: [UPGRADE_LINK]

Best regards,
[Your Company] Team
```

## 🚀 Scaling & Growth

### When to Upgrade Clients
- **Free → Basic**: When they exceed 10 documents or 1,000 requests
- **Basic → Pro**: When they need more documents or higher request limits
- **Pro → Enterprise**: When they need unlimited usage or custom features

### Revenue Optimization
- **Tiered Pricing**: Clear value progression between plans
- **Usage-Based Billing**: Charge for overages
- **Annual Discounts**: Encourage longer commitments
- **Custom Plans**: For enterprise clients

### Client Retention
- **Proactive Monitoring**: Alert before limits are reached
- **Regular Check-ins**: Monthly usage reviews
- **Feature Updates**: Keep clients engaged
- **Support Quality**: Quick response times

## 📊 Analytics & Reporting

### Key Metrics to Track
- **Client Acquisition**: New clients per month
- **Revenue**: Monthly recurring revenue (MRR)
- **Churn Rate**: Client retention
- **Usage Patterns**: Peak usage times
- **Support Tickets**: Common issues

### Monthly Client Report
```
📊 Monthly Report - [Client Name]

Usage Summary:
- Total Requests: X
- Total Documents: Y
- Average Response Time: Zms
- Uptime: 99.9%

Plan Status: [PLAN] - [STATUS]
Next Billing: [DATE]

Recommendations:
- [UPGRADE/DOWNGRADE] plan
- [ADDITIONAL] features
- [OPTIMIZATION] suggestions
```

This comprehensive guide ensures smooth client delivery and ongoing success for your ChatBot SaaS business!
