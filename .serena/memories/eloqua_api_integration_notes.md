# Oracle Eloqua API Integration Notes

## Authentication Methods
- **OAuth 2.0**: Recommended for production (client credentials flow)
- **Basic Authentication**: For development/testing
- **API Key**: Alternative authentication method

## Core API Endpoints
- **Contacts**: `/api/REST/1.0/data/contacts`
- **Campaigns**: `/api/REST/1.0/assets/campaigns`
- **Email Groups**: `/api/REST/1.0/assets/emailGroups`
- **Forms**: `/api/REST/1.0/assets/forms`
- **Landing Pages**: `/api/REST/1.0/assets/landingPages`

## Rate Limiting
- Default: 1000 requests per hour per user
- Configurable based on Eloqua instance
- Implement exponential backoff for retries
- Monitor rate limit headers in responses

## Response Formats
- JSON format for all responses
- Pagination using `page`, `count`, and `totalResults`
- Error responses include `errorCode` and `message`

## Security Considerations
- Store credentials in environment variables
- Use HTTPS for all API calls
- Implement proper token refresh logic
- Log security events appropriately

## Common Patterns
- Bulk operations for large datasets
- Asynchronous operations for long-running tasks
- Field mapping for custom fields
- Validation before API calls

## Error Handling
- 401: Authentication failure
- 403: Insufficient permissions
- 404: Resource not found
- 429: Rate limit exceeded
- 500: Server error