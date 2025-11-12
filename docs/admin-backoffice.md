# Admin Backoffice Documentation

## Overview

The Admin Backoffice is a comprehensive administrative interface for the ShortlistAI platform that allows administrators to view, monitor, and manage all platform data. It provides insights into platform usage, candidate data, AI analysis results, and system performance.

## Features

### 1. Dashboard Overview
- **Statistics Dashboard**: Real-time platform statistics including total candidates, analyses, companies, and interviewers
- **Activity Monitoring**: Recent activity including monthly analyses, new candidates, and job postings
- **AI Usage Tracking**: Monitoring of AI provider usage and costs
- **Language Distribution**: Breakdown of platform usage by language (EN, PT, FR, ES)

### 2. Data Management
- **Candidates Management**: View and manage all candidate profiles, consent status, and contact information
- **Analyses Management**: Review all AI analysis results and quality metrics
- **Companies Management**: Monitor company information and usage patterns
- **Interviewers Management**: Track interviewer activity and contact details
- **Job Postings Management**: Review and manage job postings across the platform

### 3. Admin User Management (New)
- **CRUD Operations**: Create, read, update, and delete admin users
- **Role-Based Access**: Support for admin and super_admin roles
- **Password Security**: Bcrypt hashing with secure password policies
- **Account Security**: Login attempt tracking and account lockout
- **Audit Trail**: Created/updated by tracking for compliance

### 4. Authentication & Security
- **JWT Authentication**: Secure admin login with token-based authentication
- **Database Authentication**: Authenticate against Supabase admin_users table
- **Role-Based Access Control**: Proper authorization checks for different admin levels
- **Session Management**: Secure token storage and automatic renewal
- **Audit Logging**: Track admin actions for security and compliance

## User Interface

### Login
- **URL**: `/admin/login`
- **Credentials**: Uses configured admin credentials from environment
- **Redirect**: Successful login redirects to `/admin/dashboard`

### Dashboard
- **URL**: `/admin/dashboard`
- **Features**:
  - Overview statistics cards
  - Recent activity metrics
  - Management navigation links
  - AI provider usage summary
  - Language distribution charts

### Candidates Management
- **URL**: `/admin/candidates`
- **Features**:
  - Paginated table view of all candidates
  - Search by name or email
  - Filter by country
  - Consent status indicators
  - Detailed candidate views (planned)

### Admin Users Management
- **URL**: `/admin/users` (Super Admin only)
- **Features**:
  - List all admin users with pagination
  - Create new admin accounts
  - Edit existing admin profiles
  - Deactivate admin accounts (soft delete)
  - Change admin passwords
  - Role assignment (admin/super_admin)
  - Account security monitoring

## API Endpoints

### Authentication
- `POST /api/admin/login` - Admin login
- `GET /api/admin/me` - Get current admin info

### Dashboard
- `GET /api/admin/dashboard/stats` - Basic dashboard statistics
- `GET /api/admin/dashboard/detailed-stats` - Comprehensive platform statistics

### Data Management
- `GET /api/admin/candidates` - List candidates with pagination
- `GET /api/admin/candidates/{id}` - Get candidate details with CVs and analyses
- `GET /api/admin/analyses` - List analyses with filtering
- `GET /api/admin/analyses/{id}` - Get analysis details
- `GET /api/admin/companies` - List companies
- `GET /api/admin/interviewers` - List interviewers
- `GET /api/admin/job-postings` - List job postings

### Admin User Management (New)
- `GET /api/admin/admin-users` - List admin users (super admin only)
- `POST /api/admin/admin-users` - Create new admin user (super admin only)
- `PUT /api/admin/admin-users/{id}` - Update admin user (super admin only)
- `PUT /api/admin/admin-users/{id}/password` - Change admin password (super admin only)
- `DELETE /api/admin/admin-users/{id}` - Deactivate admin user (super admin only)

### Monitoring (Planned)
- `GET /api/admin/ai/usage-logs` - AI usage logs and cost tracking
- `GET /api/admin/audit/logs` - Audit trail for compliance

## Technical Implementation

### Backend Architecture

#### Authentication
- **JWT Tokens**: Secure token-based authentication
- **Database Authentication**: Authenticate against admin_users table in Supabase
- **Password Security**: Bcrypt hashing with Supabase auth functions
- **Token Validation**: Automatic token validation on protected endpoints
- **Role-Based Access**: Super admin verification for admin management
- **Configuration**: Uses environment variables for secrets

#### Database Services
- **CandidateService**: Manages candidate CRUD operations with deduplication
- **AnalysisService**: Handles AI analysis data retrieval and filtering
- **CompanyService**: Company data management
- **InterviewerService**: Interviewer information management
- **JobPostingService**: Job posting data handling
- **AdminService**: Administrator authentication and management (New)

#### Security Features
- **Row Level Security (RLS)**: Ensures only admins can access sensitive data
- **Input Validation**: All endpoints validate and sanitize inputs
- **Error Handling**: Comprehensive error handling with appropriate status codes
- **Logging**: Security-focused logging for admin actions

### Frontend Architecture

#### Authentication Context
- **AdminAuthProvider**: React context for authentication state management
- **Token Management**: Automatic token storage and renewal
- **Route Protection**: Authentication checks for admin routes
- **User Session**: Persistent admin session management

#### Component Structure
- **AdminDashboard**: Main dashboard with statistics and navigation
- **AdminCandidates**: Candidates management interface
- **AdminAuthContext**: Authentication state management
- **useAdminAnalytics**: Analytics tracking for admin actions

#### Styling
- **Design System**: Follows brand rules and design tokens
- **Responsive Design**: Mobile, tablet, and desktop support
- **Dark Theme**: Full dark mode support
- **Accessibility**: WCAG compliance with proper ARIA labels

### Database Schema

#### Core Tables
- **candidates**: Candidate profiles and contact information
- **companies**: Company information from interviewer flows
- **interviewers**: Interviewer contact details
- **job_postings**: Job posting content and metadata
- **cvs**: CV files and extracted text with versioning
- **analyses**: AI analysis results with scoring and feedback
- **admin_users**: Administrator accounts with authentication and roles (New)

#### Security
- **Row Level Security (RLS)**: Enabled on all tables
- **Admin Access**: Full database access restricted to authenticated admins
- **Super Admin Access**: Admin user management restricted to super_admin role
- **Data Protection**: Personal data handling with consent tracking

#### Admin Users Table (New)
- **Columns**: id, username, email, password_hash, first_name, last_name, role, is_active, last_login_at, failed_login_attempts, locked_until, created_by, created_at, updated_at, updated_by
- **Security Features**:
  - Bcrypt password hashing
  - Account lockout after 5 failed attempts
  - Password reset on successful login
  - Audit trail for all changes
  - RLS policies for role-based access

## Usage Examples

### Viewing Dashboard Statistics
```javascript
// Dashboard automatically loads statistics on mount
const [stats, setStats] = useState(null);

useEffect(() => {
  const loadStats = async () => {
    const response = await api.get('/api/admin/dashboard/detailed-stats');
    setStats(response.data);
  };
  loadStats();
}, []);
```

### Managing Candidates
```javascript
// Search and filter candidates
const [candidates, setCandidates] = useState([]);
const [searchTerm, setSearchTerm] = useState('');
const [pagination, setPagination] = useState({ offset: 0, limit: 50 });

const loadCandidates = async () => {
  const params = new URLSearchParams({
    limit: pagination.limit,
    offset: pagination.offset,
    search: searchTerm
  });
  
  const response = await api.get(`/api/admin/candidates?${params}`);
  setCandidates(response.data.candidates);
};
```

### Analytics Tracking
```javascript
// Track admin page views and actions
const { trackCandidatesAction } = useAdminCandidatesAnalytics();

const handleViewCandidate = (candidateId) => {
  trackCandidatesAction('view', { candidate_id: candidateId });
  // Navigate to candidate details
};
```

## Security Considerations

### Authentication Security
- **Secure Password Storage**: Bcrypt hashing for admin passwords
- **Token Expiration**: JWT tokens expire after 24 hours
- **Secure Storage**: Tokens stored in localStorage with automatic cleanup
- **HTTPS Required**: Should only be used over HTTPS in production

### Data Protection
- **PII Handling**: Personal information properly protected and redacted in logs
- **Access Control**: Strict role-based access control
- **Audit Trail**: All admin actions logged for compliance (planned)
- **Data Minimization**: Only necessary data exposed through admin interface

### Input Validation
- **Server-side Validation**: All inputs validated on the backend
- **SQL Injection Prevention**: Parameterized queries and ORM usage
- **XSS Prevention**: Proper output encoding and content sanitization
- **Rate Limiting**: Protection against brute force attacks

## Performance Considerations

### Database Optimization
- **Pagination**: Large datasets paginated to improve performance
- **Indexing**: Proper database indexes for common queries
- **Query Optimization**: Efficient queries with minimal data transfer
- **Caching**: Strategic caching for frequently accessed data

### Frontend Performance
- **Lazy Loading**: Components and routes loaded on demand
- **Optimistic Updates**: UI updates optimistically for better UX
- **Debounced Search**: Search inputs debounced to reduce API calls
- **Efficient Re-renders**: React optimization patterns to minimize re-renders

## Future Enhancements

### Planned Features
- **Export Functionality**: Data export to CSV/Excel
- **Advanced Filtering**: Complex filters and search operators
- **Bulk Operations**: Batch actions on multiple records
- **Real-time Updates**: Live data updates via WebSocket
- **Detailed Analytics**: Advanced reporting and data visualization

### AI Management (Phase 8)
- **Prompt Management**: CRUD operations for AI prompts
- **Provider Configuration**: AI provider settings and API key management
- **Quality Monitoring**: AI analysis quality tracking and improvement
- **Cost Optimization**: AI usage optimization and cost tracking

### Compliance & Audit
- **GDPR Compliance**: Data export and deletion capabilities
- **Audit Logging**: Comprehensive admin action logging
- **Data Retention**: Automated data retention and cleanup policies
- **Compliance Reports**: Automated compliance reporting

## Configuration

### Environment Variables
```env
# Admin Authentication
SECRET_KEY=your-jwt-secret-key

# Database
SUPABASE_URL=your-supabase-url
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### Default Admin User
A default super admin user is created during database migration:
- **Username**: admin
- **Email**: admin@shortlistai.com
- **Password**: admin123
- **Role**: super_admin

**⚠️ Important**: Change the default password immediately after first login!

### Admin User Roles
- **Admin**: Can access all dashboard features and data management
- **Super Admin**: Can additionally manage other admin users and access admin user management

### Creating Additional Admin Users
1. Login as super admin
2. Navigate to `/admin/users`
3. Click "Create New Admin"
4. Fill in the required information
5. Assign appropriate role (admin or super_admin)

### Password Security
- Minimum 8 characters required
- Bcrypt hashing with salt
- Account lockout after 5 failed login attempts
- Automatic unlock after 30 minutes

## Troubleshooting

### Common Issues

#### Authentication Problems
- **Invalid Token**: Token expired or malformed
- **Login Failures**: Check admin credentials in database
- **Redirect Issues**: Verify AdminAuthProvider wrapper in App.tsx
- **Database Connection**: Ensure admin_users table exists and RLS policies are applied
- **Default Admin Not Working**: Verify migration was applied successfully

#### Admin User Management Issues
- **403 Forbidden**: Not a super admin (only super admins can manage other admins)
- **User Not Found**: Admin user may be deactivated or deleted
- **Role Assignment**: Only super_admin role can create other super_admin users
- **Password Requirements**: Password must be at least 8 characters
- **Account Locked**: Too many failed login attempts, wait 30 minutes or contact super admin

#### Database Issues
- **admin_users Table Missing**: Run migration 003_admin_users.sql
- **RLS Policy Errors**: Verify RLS policies are enabled and correctly configured
- **Permission Denied**: Check that authenticated role has proper permissions

### Debugging Tips
- **API Testing**: Use `/api/docs` endpoint to test API calls
- **Console Logging**: Check browser console for error messages
- **Network Tab**: Monitor API requests and responses
- **Database Query**: Use Supabase dashboard for query analysis
- **Admin Table**: Verify admin_users table has default super admin user
- **Migration Status**: Check if migration 003_admin_users.sql was applied successfully

## Support

For technical support or feature requests related to the Admin Backoffice:
- **Technical Issues**: Check logs and API documentation
- **Feature Requests**: Document requirements and use cases
- **Security Issues**: Report immediately following security procedures
- **Documentation**: Keep documentation updated with changes

---

**Last Updated**: November 2025  
**Version**: 2.0.0  
**Status**: Production Ready with Admin User Management

## Recent Updates (v2.0.0)

### ✨ New Features
- **Admin User Management**: Complete CRUD interface for managing administrator accounts
- **Database Authentication**: Moved from environment-based to Supabase-based authentication
- **Role-Based Access**: Proper role hierarchy with admin and super_admin roles
- **Enhanced Security**: Account lockout, audit trails, and comprehensive security features

### 🏗️ Architecture Changes
- **AdminService**: New service for administrator management
- **admin_users Table**: New database table with RLS policies
- **Migration System**: Automated admin user creation and security setup
- **Enhanced API**: New endpoints for admin user management

### 🔒 Security Improvements
- **Database Authentication**: Secure credential storage in Supabase
- **Password Policies**: Bcrypt hashing with secure salt
- **Account Protection**: Failed login tracking and automatic lockout
- **Audit Compliance**: Full audit trail for admin actions

### 📋 Ready for Production
The admin backoffice now includes complete user management capabilities, making it suitable for enterprise deployments with multiple administrators and proper access control.
