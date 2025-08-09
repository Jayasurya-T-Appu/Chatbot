# Admin Security Guide

## 🔐 Admin Authentication

The ChatBot Plugin now has a secure admin authentication system to protect the admin dashboard.

### How It Works

1. **Login Page**: `/admin` - Requires admin API key to access
2. **Dashboard**: `/admin-dashboard` - Protected dashboard (requires authentication)
3. **API Key**: Stored securely in browser localStorage after successful login

### Security Features

- ✅ **Protected Routes**: Admin dashboard requires valid API key
- ✅ **Session Management**: API key stored in localStorage for convenience
- ✅ **Auto Logout**: Invalid/expired sessions redirect to login
- ✅ **Secure Storage**: API key stored as password field (hidden)
- ✅ **Logout Function**: Manual logout clears stored credentials

### Setup Instructions

1. **Set Admin API Key** in your `.env` file:
   ```bash
   ADMIN_API_KEY=your-secure-admin-key-here
   ```

2. **Access Admin Panel**:
   - Go to `http://localhost:8000/admin`
   - Enter your admin API key
   - Click "Login to Dashboard"

3. **Default Admin Key** (change this in production):
   ```
   admin-secret-key-12345
   ```

### Security Best Practices

1. **Use Strong API Key**: Generate a secure, random admin API key
2. **Environment Variables**: Never hardcode the admin key in source code
3. **HTTPS in Production**: Always use HTTPS for admin access in production
4. **Regular Key Rotation**: Change admin keys periodically
5. **Access Logging**: Monitor admin access logs
6. **IP Restrictions**: Consider IP whitelisting for admin access

### Production Security Checklist

- [ ] Change default admin API key
- [ ] Enable HTTPS
- [ ] Set up proper logging
- [ ] Configure firewall rules
- [ ] Use environment variables
- [ ] Regular security audits
- [ ] Backup admin credentials securely

### Troubleshooting

**"Session expired" error**: 
- Clear browser localStorage
- Re-login with valid API key

**Cannot access admin dashboard**:
- Verify admin API key in `.env` file
- Check server is running
- Ensure correct URL (`/admin` not `/admin-dashboard`)

### API Endpoints

- `GET /admin` - Login page (public)
- `GET /admin-dashboard` - Dashboard (requires auth)
- `POST /admin/clients` - Create client (requires auth)
- `GET /admin/clients` - List clients (requires auth)
- `DELETE /admin/clients/{id}` - Delete client (requires auth)

All admin API endpoints require the `Authorization: Bearer {admin_key}` header.
