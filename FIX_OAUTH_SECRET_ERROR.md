# 🔧 Fix OAuth Secret Error

## ❌ Current Error
```json
{
  "code": 400,
  "error_code": "validation_failed",
  "msg": "Unsupported provider: missing OAuth secret"
}
```

## 🎯 Root Cause

You enabled Google OAuth in Supabase, but you didn't add the **Client ID** and **Client Secret** from Google Cloud Console.

---

## ✅ Complete Fix (5 Minutes)

### Step 1: Create Google OAuth Credentials (3 min)

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/

2. **Create a New Project** (or select existing):
   - Click "Select a project" → "New Project"
   - Name: "ISAVS Attendance"
   - Click "Create"

3. **Enable Google+ API:**
   - Go to: https://console.cloud.google.com/apis/library
   - Search for "Google+ API"
   - Click "Enable"

4. **Create OAuth Credentials:**
   - Go to: https://console.cloud.google.com/apis/credentials
   - Click "Create Credentials" → "OAuth client ID"
   - If prompted, configure OAuth consent screen first:
     - User Type: External
     - App name: "ISAVS Attendance"
     - User support email: your-email@gmail.com
     - Developer contact: your-email@gmail.com
     - Click "Save and Continue" (skip optional fields)
   
5. **Configure OAuth Client:**
   - Application type: **Web application**
   - Name: "ISAVS Web Client"
   
6. **Add Authorized Redirect URIs:**
   ```
   https://textjheeqfwmrzjtfdyo.supabase.co/auth/v1/callback
   http://localhost:3001/auth/callback
   ```
   
7. **Click "Create"**
   - **Copy the Client ID** (looks like: `123456789-abc.apps.googleusercontent.com`)
   - **Copy the Client Secret** (looks like: `GOCSPX-abc123xyz`)
   - **SAVE THESE!** You'll need them in the next step

---

### Step 2: Add Credentials to Supabase (2 min)

1. **Go to Supabase Dashboard:**
   - Visit: https://supabase.com/dashboard/project/textjheeqfwmrzjtfdyo/auth/providers

2. **Find Google Provider:**
   - Scroll to "Google" section
   - Make sure it's **Enabled** (toggle ON)

3. **Add Your Credentials:**
   - **Client ID**: Paste the Client ID from Google Cloud Console
   - **Client Secret**: Paste the Client Secret from Google Cloud Console

4. **Add Redirect URL:**
   ```
   http://localhost:3001/auth/callback
   ```

5. **Click "Save"**

---

### Step 3: Test Login (30 seconds)

1. Go to: http://localhost:3001
2. Click any portal (Student, Teacher, or Admin)
3. Click "Continue with Gmail"
4. Should work now! ✅

---

## 📋 Quick Checklist

- [ ] Created Google Cloud Project
- [ ] Enabled Google+ API
- [ ] Created OAuth Client ID
- [ ] Added redirect URIs in Google Cloud Console
- [ ] Copied Client ID and Client Secret
- [ ] Pasted credentials in Supabase
- [ ] Enabled Google provider in Supabase
- [ ] Added redirect URL in Supabase
- [ ] Saved changes
- [ ] Tested login

---

## 🎯 Visual Guide

### Google Cloud Console

```
1. Create Project
   ┌─────────────────────────────────┐
   │ Project Name: ISAVS Attendance  │
   │ [Create]                        │
   └─────────────────────────────────┘

2. Enable Google+ API
   ┌─────────────────────────────────┐
   │ Google+ API                     │
   │ [Enable]                        │
   └─────────────────────────────────┘

3. Create OAuth Client
   ┌─────────────────────────────────┐
   │ Application type: Web app       │
   │ Name: ISAVS Web Client          │
   │                                 │
   │ Authorized redirect URIs:       │
   │ https://textjheeqfwmrzjtfdyo... │
   │ http://localhost:3001/auth/...  │
   │                                 │
   │ [Create]                        │
   └─────────────────────────────────┘

4. Copy Credentials
   ┌─────────────────────────────────┐
   │ Client ID:                      │
   │ 123456789-abc.apps.google...    │
   │                                 │
   │ Client Secret:                  │
   │ GOCSPX-abc123xyz                │
   │                                 │
   │ [Copy] [Copy]                   │
   └─────────────────────────────────┘
```

### Supabase Dashboard

```
Authentication → Providers → Google

┌─────────────────────────────────────┐
│ Google                              │
│ [●] Enabled                         │
│                                     │
│ Client ID (from Google):            │
│ [123456789-abc.apps.google...]      │
│                                     │
│ Client Secret (from Google):        │
│ [GOCSPX-abc123xyz]                  │
│                                     │
│ Redirect URL:                       │
│ [http://localhost:3001/auth/...]    │
│                                     │
│ [Save]                              │
└─────────────────────────────────────┘
```

---

## 🔍 Troubleshooting

### Error: "redirect_uri_mismatch"
**Solution:** Make sure you added the exact redirect URI in Google Cloud Console:
```
https://textjheeqfwmrzjtfdyo.supabase.co/auth/v1/callback
```

### Error: "Access blocked: This app's request is invalid"
**Solution:** Configure OAuth consent screen in Google Cloud Console

### Error: "Invalid client"
**Solution:** Double-check Client ID and Client Secret are correct

### Still getting "missing OAuth secret"
**Solution:** 
1. Clear browser cache
2. Restart frontend server
3. Try incognito mode

---

## 💡 Alternative: Use Email/Password (Quick Demo)

If you want to skip OAuth for now and just demo the system, you can use email/password authentication:

### Enable Email Auth in Supabase

1. Go to: https://supabase.com/dashboard/project/textjheeqfwmrzjtfdyo/auth/providers
2. Find "Email" provider
3. Enable it
4. Save

### Create Test Users

Run this SQL in Supabase:

```sql
-- Create test users
INSERT INTO auth.users (
  instance_id,
  id,
  aud,
  role,
  email,
  encrypted_password,
  email_confirmed_at,
  created_at,
  updated_at
) VALUES (
  '00000000-0000-0000-0000-000000000000',
  gen_random_uuid(),
  'authenticated',
  'authenticated',
  'admin@demo.com',
  crypt('password123', gen_salt('bf')),
  now(),
  now(),
  now()
);

-- Repeat for teacher@demo.com and student@demo.com
```

### Update Login Pages

Add email/password inputs to login pages (I can do this if you want).

---

## 🎯 Recommended Approach

**For Hackathon Demo:** Use Google OAuth (5 min setup)
- More impressive
- Professional
- Real authentication

**For Quick Testing:** Use email/password (2 min setup)
- Faster
- No Google Cloud setup needed
- Good for development

---

## 📝 Summary

**The error means:** Supabase needs Google OAuth credentials

**The fix:**
1. Create OAuth credentials in Google Cloud Console (3 min)
2. Add credentials to Supabase (2 min)
3. Test login (30 sec)

**Total time: 5 minutes** ⏱️

---

## 🚀 After Fixing

Once OAuth is configured, you can:
1. Login with any Gmail account
2. Assign roles in database
3. Test all three portals
4. Demo the system

---

**Need help? Follow the steps above carefully, and it will work!** ✅

---

## 📞 Quick Links

- **Google Cloud Console**: https://console.cloud.google.com/
- **Supabase Auth Settings**: https://supabase.com/dashboard/project/textjheeqfwmrzjtfdyo/auth/providers
- **Google OAuth Guide**: https://supabase.com/docs/guides/auth/social-login/auth-google

---

**This is the complete fix! Follow these steps and OAuth will work perfectly!** 🎉
