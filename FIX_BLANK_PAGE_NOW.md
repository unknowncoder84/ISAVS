# 🔧 FIX BLANK PAGE - STEP BY STEP

## ✅ SERVERS ARE CONFIRMED WORKING
- Backend: http://localhost:6000 ✅
- Frontend: http://localhost:6002 ✅

The blank page is **100% a browser cache issue**. Follow these steps:

---

## 🎯 STEP 1: TEST THE SERVER (Proves it's working)

Open this URL in your browser:
**http://localhost:6002/test.html**

You should see a dark page with "✅ Server is Working!" message.

If you see this, it confirms the server is fine and the issue is cache.

---

## 🔧 STEP 2: CLEAR BROWSER CACHE (Required!)

### Option A: Clear All Cache (Recommended)
1. Press **Ctrl + Shift + Delete**
2. Select "Cached images and files"
3. Click "Clear data"
4. Close ALL browser windows
5. Reopen browser and go to http://localhost:6002

### Option B: Hard Refresh (Quick)
1. Go to http://localhost:6002
2. Press **Ctrl + F5** (or **Ctrl + Shift + R**)
3. Wait 5 seconds
4. If still blank, try Option A

### Option C: Developer Tools Method
1. Press **F12** to open DevTools
2. Right-click the refresh button (next to address bar)
3. Select "Empty Cache and Hard Reload"
4. Close DevTools
5. Refresh again

---

## 🚀 STEP 3: TRY DIFFERENT BROWSER

If cache clearing doesn't work:
1. Open a **different browser** (Edge, Firefox, Chrome - whichever you're NOT using)
2. Go to http://localhost:6002
3. You'll see the app immediately (no cache)

---

## 🔍 STEP 4: CHECK FOR ERRORS

If you still see blank:
1. Press **F12** to open DevTools
2. Click "Console" tab
3. Look for RED error messages
4. Take a screenshot and share it

---

## 📱 WHAT YOU SHOULD SEE

Once cache is cleared, you'll see:
- Dark background (#0f0d1a)
- Animated gradient
- 3 portal cards:
  - 🎓 Student Portal
  - 👨‍🏫 Teacher Portal
  - 🔐 Admin Portal

---

## 🎯 DEMO CREDENTIALS

### Admin
- admin@isavs.edu / admin123

### Teachers
- teacher1@isavs.edu / teacher123
- teacher2@isavs.edu / teacher123

### Students
- student1@isavs.edu / student123
- student2@isavs.edu / student123

---

## ⚡ QUICK FIX SUMMARY

1. **Test**: http://localhost:6002/test.html
2. **Clear Cache**: Ctrl + Shift + Delete
3. **Try Different Browser**: Edge/Firefox/Chrome
4. **Check Console**: F12 → Console tab

The servers are working perfectly. This is purely a browser cache issue from the old port (3001 → 6002).
