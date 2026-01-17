# 🎓 Deploy Student Kiosk to Netlify

## 📋 Two Deployment Options

### Option 1: Separate Repository Branch (Recommended)
Create a `student` branch with student-specific index.html

### Option 2: Separate Netlify Site (Easiest)
Deploy from the same repo but with different build settings

---

## 🚀 Option 1: Using Git Branches (Recommended)

### Step 1: Create Student Branch
```bash
# Create and switch to student branch
git checkout -b student

# Update index.html for student
# (see below)

# Commit changes
git commit -am "Configure for student kiosk deployment"

# Push student branch
git push -u origin student
```

### Step 2: Update index.html for Student
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>ISAVS 2026 - Student Kiosk</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main-student.tsx"></script>
  </body>
</html>
```

### Step 3: Deploy to Netlify
1. Go to Netlify dashboard
2. Click "Add new site" → "Import an existing project"
3. Select: `unknowncoder84/ISAVS`
4. **Important:** Select branch: `student` (not main)
5. Configure:
   ```
   Base directory: frontend
   Build command: npm run build:student
   Publish directory: frontend/dist
   ```
6. Add environment variables (same as teacher)
7. Deploy!

### Benefits
- ✅ Clean separation between teacher and student
- ✅ Can update independently
- ✅ Easy to maintain
- ✅ No conflicts

---

## 🚀 Option 2: Same Repo, Different Site (Easiest)

### Step 1: Create Second Netlify Site
1. Go to Netlify dashboard
2. Click "Add new site" → "Import an existing project"
3. Select: `unknowncoder84/ISAVS` (same repo)
4. Branch: `main`

### Step 2: Configure Build Settings
```
Site name: isavs-student-kiosk
Base directory: frontend
Build command: npm run build:student
Publish directory: frontend/dist
```

### Step 3: Add Build Hook
Since both sites use the same repo, we need to ensure the correct entry point is used.

**Add this to your build command:**
```bash
sed -i 's/main-teacher/main-student/g' index.html && npm run build:student
```

Or better, use a custom build script.

### Step 4: Environment Variables
Add the same variables as teacher site:
```
VITE_API_URL=https://your-backend-url.com
VITE_SUPABASE_URL=https://textjheeqfwmrzjtfdyo.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key
```

---

## 🎯 Quick Setup (Recommended Approach)

I'll create a build script that automatically switches based on the build command:

### Step 1: Create Build Scripts

**File: `frontend/build-teacher.sh`**
```bash
#!/bin/bash
# Update index.html for teacher
sed -i 's/main-student/main-teacher/g' index.html
sed -i 's/Student Kiosk/Teacher Dashboard/g' index.html
npm run build:teacher
```

**File: `frontend/build-student.sh`**
```bash
#!/bin/bash
# Update index.html for student
sed -i 's/main-teacher/main-student/g' index.html
sed -i 's/Teacher Dashboard/Student Kiosk/g' index.html
npm run build:student
```

### Step 2: Update package.json
```json
{
  "scripts": {
    "build:teacher:netlify": "bash build-teacher.sh",
    "build:student:netlify": "bash build-student.sh"
  }
}
```

### Step 3: Netlify Configuration

**Teacher Site:**
- Build command: `npm run build:teacher:netlify`

**Student Site:**
- Build command: `npm run build:student:netlify`

---

## 💡 Simplest Solution (What I Recommend)

### Create Two Separate index.html Files

**File: `frontend/index-teacher.html`**
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>ISAVS 2026 - Teacher Dashboard</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main-teacher.tsx"></script>
  </body>
</html>
```

**File: `frontend/index-student.html`**
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>ISAVS 2026 - Student Kiosk</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main-student.tsx"></script>
  </body>
</html>
```

### Update package.json
```json
{
  "scripts": {
    "build:teacher:netlify": "cp index-teacher.html index.html && npm run build:teacher",
    "build:student:netlify": "cp index-student.html index.html && npm run build:student"
  }
}
```

### Netlify Configuration

**Teacher Site:**
```
Build command: npm run build:teacher:netlify
```

**Student Site:**
```
Build command: npm run build:student:netlify
```

---

## 🎯 Step-by-Step: Deploy Student Site Now

### 1. Go to Netlify Dashboard
https://app.netlify.com

### 2. Add New Site
- Click "Add new site"
- Choose "Import an existing project"
- Select GitHub
- Choose: `unknowncoder84/ISAVS`

### 3. Configure Build
```
Site name: isavs-student-kiosk
Branch: main
Base directory: frontend
Build command: cp index-student.html index.html && npm run build:student
Publish directory: frontend/dist
```

### 4. Environment Variables
```
VITE_API_URL=https://your-backend-url.com
VITE_SUPABASE_URL=https://textjheeqfwmrzjtfdyo.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGc...
```

### 5. Deploy!
Click "Deploy site"

---

## 📊 Summary

### Current Setup
- **Teacher Site:** Uses `index.html` with `main-teacher.tsx`
- **Student Site:** Needs `index.html` with `main-student.tsx`

### Solution
Create `index-student.html` and use build command to copy it before building.

### Your Sites Will Be
- **Teacher:** `https://isavs-teacher.netlify.app`
- **Student:** `https://isavs-student.netlify.app`

---

## 🔧 Let Me Set This Up For You

I'll create the necessary files now...
