/**
 * Niya - TuitionTrack Help Bot
 * Cheerful and welcoming option-based help assistant
 */

const NiyaHelpBot = {
    // User role (tutor or student)
    userRole: 'tutor',
    
    // Help content structure - Tutor version
    contentTutor: {
        main: {
            message: "Hi! I'm Niya 👋\n\nI'm here to help you with TuitionTrack! What would you like to know?",
            options: [
                { text: "📊 Attendance", action: "attendance" },
                { text: "👥 Students", action: "students" },
                { text: "📝 Homework", action: "homework" },
                { text: "📚 Batches", action: "batches" },
                { text: "📈 Reports", action: "reports" },
                { text: "🚀 Getting Started", action: "getting_started" },
                { text: "🔧 Troubleshooting", action: "troubleshooting" },
                { text: "👤 Account & Security", action: "account" },
                { text: "🎓 Student Portal", action: "student_portal" },
                { text: "🔔 Notifications", action: "notifications" },
                { text: "⚙️ Profile & Settings", action: "profile" },
                { text: "❓ General Help", action: "general" }
            ]
        },
        attendance: {
            message: "Great! Let's talk about attendance 📊\n\nWhat do you need help with?",
            options: [
                { text: "How to mark attendance", action: "attendance_mark" },
                { text: "View attendance history", action: "attendance_view" },
                { text: "Fix attendance mistake", action: "attendance_fix" },
                { text: "Attendance reports", action: "attendance_reports" },
                { text: "🔙 Back", action: "main" },
                { text: "👋 Close", action: "close" }
            ]
        },
        attendance_mark: {
            message: "Marking attendance is super easy! ✨\n\n📋 Steps:\n1. Go to the 'Attendance' tab\n2. Select the date (or use today's date)\n3. For each student, click:\n   • ✅ Present - Student is present\n   • ❌ Absent - Student is absent\n   • ⏰ Late - Student came late\n4. Click 'Save Attendance' button\n\n💡 Tip: You can mark attendance for multiple students at once!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "Still need help", action: "contact" },
                { text: "🔙 Back", action: "attendance" },
                { text: "👋 Close", action: "close" }
            ]
        },
        attendance_view: {
            message: "Viewing attendance history 📅\n\nFor Tutors:\n• Go to 'Reports' tab\n• Click on any batch to see attendance\n• Click on a student to see their 30-day attendance grid\n\nFor Students:\n• Go to 'Attendance' tab\n• See your monthly attendance grid\n• Green = Present, Red = Absent, Yellow = Late",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "attendance" },
                { text: "👋 Close", action: "close" }
            ]
        },
        attendance_fix: {
            message: "Need to fix attendance? No worries! 😊\n\nTo correct attendance:\n1. Go to 'Attendance' tab\n2. Select the date you want to fix\n3. Change the status (Present/Absent/Late)\n4. Click 'Save Attendance'\n\n✅ Your changes will be saved immediately!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "attendance" },
                { text: "👋 Close", action: "close" }
            ]
        },
        attendance_reports: {
            message: "Attendance Reports 📈\n\nTutors can:\n• View batch-wise attendance summary\n• See individual student attendance (30-day grid)\n• Track attendance patterns\n\nStudents can:\n• View their own attendance grid\n• See monthly attendance summary\n\n💡 All reports show current month only for clean data!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "attendance" },
                { text: "👋 Close", action: "close" }
            ]
        },
        students: {
            message: "Student Management 👥\n\nWhat would you like to know?",
            options: [
                { text: "Add a student", action: "students_add" },
                { text: "Edit student info", action: "students_edit" },
                { text: "Delete a student", action: "students_delete" },
                { text: "View student details", action: "students_view" },
                { text: "Search students", action: "students_search" },
                { text: "🔙 Back", action: "main" }
            ]
        },
        students_add: {
            message: "Adding a new student is easy! 🎓\n\n📋 Steps:\n1. Go to 'Students' tab\n2. Click 'Add New Student' button\n3. Fill in the details:\n   • Name (required)\n   • Phone number (required)\n   • Batch (required - select or create new)\n   • Address (optional)\n   • School name (optional)\n   • Class/Standard (optional)\n4. Click 'Add Student'\n\n💡 The student will receive a password automatically!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "students" },
                { text: "👋 Close", action: "close" }
            ]
        },
        students_edit: {
            message: "Editing student information ✏️\n\n📋 Steps:\n1. Go to 'Students' tab\n2. Find the student you want to edit\n3. Click the 'Edit' button\n4. Update any information\n5. Click 'Save Changes'\n\n💡 You can change everything except the phone number!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "students" },
                { text: "👋 Close", action: "close" }
            ]
        },
        students_delete: {
            message: "Deleting a student 🗑️\n\n⚠️ Important:\n• This will remove the student permanently\n• All their attendance and homework data will be deleted\n• This action cannot be undone\n\n📋 Steps:\n1. Go to 'Students' tab\n2. Find the student\n3. Click 'Delete' button\n4. Confirm the deletion\n\n💡 Make sure you really want to delete before confirming!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "students" },
                { text: "👋 Close", action: "close" }
            ]
        },
        students_view: {
            message: "Viewing student details 👤\n\n📋 Steps:\n1. Go to 'Students' tab\n2. Click on any student card\n3. You'll see:\n   • Complete student information\n   • Recent attendance records\n   • Assigned batch details\n\n💡 Students can view their own profile in the student portal!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "students" },
                { text: "👋 Close", action: "close" }
            ]
        },
        students_search: {
            message: "Searching for students 🔍\n\n📋 How to search:\n1. Go to 'Students' tab\n2. Use the search box at the top\n3. Type student name or phone number\n4. Results will filter automatically\n\n💡 You can also filter by batch using the batch dropdown!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "students" },
                { text: "👋 Close", action: "close" }
            ]
        },
        homework: {
            message: "Homework Management 📝\n\nWhat would you like to know?",
            options: [
                { text: "Share homework", action: "homework_share" },
                { text: "View homework", action: "homework_view" },
                { text: "Edit homework", action: "homework_edit" },
                { text: "Delete homework", action: "homework_delete" },
                { text: "🔙 Back", action: "main" }
            ]
        },
        homework_share: {
            message: "Sharing homework with students 📚\n\n📋 Steps:\n1. Go to 'Homework' tab\n2. Click 'Share New Homework' button\n3. Fill in:\n   • Title (required)\n   • Description/Content\n   • Upload file (optional - PDF, images)\n   • Select batch or specific student\n   • Set due date\n4. Click 'Share Homework'\n\n💡 Students will get a push notification when you share homework!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "homework" },
                { text: "👋 Close", action: "close" }
            ]
        },
        homework_view: {
            message: "Viewing homework 📖\n\nFor Tutors:\n• See all homework you've shared\n• Filter by batch or student\n• View submission dates\n\nFor Students:\n• See all homework assigned to you\n• Check due dates\n• View homework details and files\n\n💡 Homework automatically deletes 1 day after due date!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "homework" },
                { text: "👋 Close", action: "close" }
            ]
        },
        homework_edit: {
            message: "Editing homework ✏️\n\n📋 Steps:\n1. Go to 'Homework' tab\n2. Find the homework you want to edit\n3. Click 'Edit' button\n4. Update title, description, or due date\n5. Click 'Save Changes'\n\n💡 You can't change the assigned batch/student after creating!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "homework" },
                { text: "👋 Close", action: "close" }
            ]
        },
        homework_delete: {
            message: "Deleting homework 🗑️\n\n📋 Steps:\n1. Go to 'Homework' tab\n2. Find the homework\n3. Click 'Delete' button\n4. Confirm deletion\n\n💡 Homework also auto-deletes 1 day after due date!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "homework" },
                { text: "👋 Close", action: "close" }
            ]
        },
        batches: {
            message: "Batch Management 📚\n\nWhat would you like to know?",
            options: [
                { text: "Create a batch", action: "batches_create" },
                { text: "Edit batch", action: "batches_edit" },
                { text: "View batch students", action: "batches_view" },
                { text: "Delete batch", action: "batches_delete" },
                { text: "🔙 Back", action: "main" }
            ]
        },
        batches_create: {
            message: "Creating a new batch 🆕\n\n📋 Steps:\n1. Go to 'Batches' tab\n2. Click 'Create New Batch' button\n3. Fill in:\n   • Batch name (e.g., 'Class 10 PCM')\n   • Description (optional)\n   • Start time (optional)\n   • End time (optional)\n4. Click 'Create Batch'\n\n💡 You can assign students to batches when adding them!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "batches" },
                { text: "👋 Close", action: "close" }
            ]
        },
        batches_edit: {
            message: "Editing a batch ✏️\n\n📋 Steps:\n1. Go to 'Batches' tab\n2. Find the batch you want to edit\n3. Click 'Edit' button\n4. Update batch name, description, or timings\n5. Click 'Save Changes'\n\n💡 Batch timings help with attendance reminders!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "batches" },
                { text: "👋 Close", action: "close" }
            ]
        },
        batches_view: {
            message: "Viewing batch students 👥\n\n📋 Steps:\n1. Go to 'Batches' tab\n2. Click on any batch card\n3. You'll see:\n   • All students in that batch\n   • Batch details and timings\n   • Quick actions\n\n💡 You can add/remove students from here!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "batches" },
                { text: "👋 Close", action: "close" }
            ]
        },
        batches_delete: {
            message: "Deleting a batch 🗑️\n\n⚠️ Important:\n• Students in this batch won't be deleted\n• They'll just be unassigned from the batch\n• You can reassign them later\n\n📋 Steps:\n1. Go to 'Batches' tab\n2. Find the batch\n3. Click 'Delete' button\n4. Confirm deletion",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "batches" },
                { text: "👋 Close", action: "close" }
            ]
        },
        reports: {
            message: "Reports & Analytics 📈\n\nWhat would you like to know?",
            options: [
                { text: "View attendance reports", action: "reports_attendance" },
                { text: "Batch summary", action: "reports_batch" },
                { text: "Student details", action: "reports_student" },
                { text: "🔙 Back", action: "main" }
            ]
        },
        reports_attendance: {
            message: "Attendance Reports 📊\n\nTutors can view:\n• Batch-wise attendance summary\n• Individual student attendance (30-day grid)\n• Monthly attendance patterns\n\nStudents can view:\n• Their own monthly attendance grid\n• Attendance status (Present/Absent/Late)\n\n💡 Reports show current month only for clean data!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "reports" },
                { text: "👋 Close", action: "close" }
            ]
        },
        reports_batch: {
            message: "Batch Summary Report 📋\n\n📋 Steps:\n1. Go to 'Reports' tab\n2. See all batches listed\n3. Click on any batch\n4. View:\n   • All students in batch\n   • 7-day attendance summary\n   • Click student to see detailed 30-day grid\n\n💡 Great for parent-teacher meetings!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "reports" },
                { text: "👋 Close", action: "close" }
            ]
        },
        reports_student: {
            message: "Student Detail Report 👤\n\n📋 Steps:\n1. Go to 'Reports' tab\n2. Click on a batch\n3. Click on a student\n4. View:\n   • 30-day attendance grid\n   • Monthly attendance summary\n   • Color indicators:\n     🟢 Green = Present\n     🔴 Red = Absent\n     🟡 Yellow = Late",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "reports" },
                { text: "👋 Close", action: "close" }
            ]
        },
        notifications: {
            message: "Notifications 🔔\n\nTuitionTrack sends you notifications for:\n• When attendance is marked (students)\n• When new homework is shared (students)\n• Batch start reminders (tutors)\n\n💡 Notifications work even when the app is closed!\n\nTo enable:\n• Allow notifications when prompted\n• They're automatically enabled on login",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "main" }
            ]
        },
        profile: {
            message: "Profile & Settings ⚙️\n\nTutors can:\n• Edit tuition name\n• Update tutor/owner name\n• Change address\n• View mobile number (can't be changed)\n\nStudents can:\n• View their profile\n• See batch information\n• View tuition details\n• Contact teacher info\n\n💡 Go to Profile tab to manage your settings!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "main" }
            ]
        },
        general: {
            message: "General Help ❓\n\nCommon questions:\n\nQ: How do I login?\nA: Use your mobile number and password\n\nQ: Can I use this on mobile?\nA: Yes! It's a PWA - works great on phones\n\nQ: Is my data safe?\nA: Yes, all data is stored securely\n\nQ: Can I use it offline?\nA: Basic features work offline\n\nNeed more help? Contact support!",
            options: [
                { text: "Contact Support", action: "contact" },
                { text: "🔙 Back", action: "main" },
                { text: "👋 Close", action: "close" }
            ]
        },
        contact: {
            message: "Contact Support 📞\n\nIf you need additional help:\n\n• Check your profile for teacher contact info\n• Email: support@tuitiontrack.com\n• Phone: Check your tuition profile\n\n💡 Most questions can be answered by exploring the app - try it out!",
            options: [
                { text: "🔙 Back to Main", action: "main" },
                { text: "👋 Close", action: "close" }
            ]
        },
    },
    
    // Help content structure - Student version
    contentStudent: {
        main: {
            message: "Hi! I'm Niya 👋\n\nI'm here to help you with TuitionTrack! What would you like to know?",
            options: [
                { text: "📊 My Attendance", action: "attendance" },
                { text: "📝 My Homework", action: "homework" },
                { text: "📚 My Batch", action: "batch" },
                { text: "👤 My Profile", action: "profile" },
                { text: "🚀 Getting Started", action: "getting_started" },
                { text: "🔧 Troubleshooting", action: "troubleshooting" },
                { text: "🔔 Notifications", action: "notifications" },
                { text: "❓ General Help", action: "general" },
                { text: "👋 Close", action: "close" }
            ]
        },
        attendance: {
            message: "Viewing Your Attendance 📊\n\n📋 Steps:\n1. Go to 'Attendance' tab\n2. See your monthly attendance grid\n\nColor indicators:\n🟢 Green = Present\n🔴 Red = Absent\n🟡 Yellow = Late\n\n💡 Your attendance is updated by your tutor!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "main" },
                { text: "👋 Close", action: "close" }
            ]
        },
        homework: {
            message: "My Homework 📝\n\n📋 Steps:\n1. Go to 'Homework' tab\n2. See all homework assigned to you\n3. Check due dates\n4. View homework details and files\n\n💡 You'll get notifications when new homework is shared!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "main" },
                { text: "👋 Close", action: "close" }
            ]
        },
        batch: {
            message: "My Batch 📚\n\n📋 Steps:\n1. Go to Dashboard\n2. Click on your batch card\n3. View batch details\n\n💡 You can see all your batch information here!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "main" },
                { text: "👋 Close", action: "close" }
            ]
        },
        profile: {
            message: "My Profile 👤\n\nYou can view:\n• Your name and contact info\n• Batch information\n• Tuition details\n• Teacher contact information\n\n💡 Go to Profile tab to see your details!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "main" },
                { text: "👋 Close", action: "close" }
            ]
        },
        getting_started: {
            message: "Getting Started 🚀\n\nWelcome to TuitionTrack Student Portal!\n\nYou can:\n• View your attendance\n• Check homework assignments\n• See batch details\n• Contact your teacher\n\n💡 Everything you need is in the tabs below!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "main" },
                { text: "👋 Close", action: "close" }
            ]
        },
        troubleshooting: {
            message: "Troubleshooting 🔧\n\nHaving issues? Try these:\n\n1. Refresh the page\n2. Check internet connection\n3. Clear browser cache\n4. Contact your teacher\n\n💡 Most issues can be fixed by refreshing!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "main" },
                { text: "👋 Close", action: "close" }
            ]
        },
        notifications: {
            message: "Notifications 🔔\n\nYou'll receive notifications for:\n• When attendance is marked\n• When new homework is shared\n\n💡 Notifications work even when the app is closed!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "main" },
                { text: "👋 Close", action: "close" }
            ]
        },
        general: {
            message: "General Help ❓\n\nCommon questions:\n\nQ: How do I login?\nA: Use your phone number and password\n\nQ: Can I use this on mobile?\nA: Yes! It works great on phones\n\nQ: Is my data safe?\nA: Yes, all data is stored securely\n\nNeed more help? Contact your teacher!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "main" },
                { text: "👋 Close", action: "close" }
            ]
        },
        contact: {
            message: "Contact Support 📞\n\nIf you need help:\n\n• Check your profile for teacher contact info\n• Contact your teacher directly\n\n💡 Your teacher can help with most questions!",
            options: [
                { text: "🔙 Back to Main", action: "main" },
                { text: "👋 Close", action: "close" }
            ]
        },
        getting_started: {
            message: "Getting Started 🚀\n\nWelcome to TuitionTrack! Let's get you set up.",
            options: [
                { text: "First time setup", action: "getting_started_setup" },
                { text: "Create account", action: "getting_started_account" },
                { text: "Add first student", action: "getting_started_student" },
                { text: "Create first batch", action: "getting_started_batch" },
                { text: "Mark first attendance", action: "getting_started_attendance" },
                { text: "Basic navigation", action: "getting_started_navigation" },
                { text: "🔙 Back", action: "main" }
            ]
        },
        getting_started_setup: {
            message: "First Time Setup 🎯\n\n📋 Quick Setup Guide:\n\n1. Create your account (mobile + password)\n2. Add your tuition name and details\n3. Create your first batch\n4. Add students to the batch\n5. Start marking attendance!\n\n💡 Take it one step at a time - I'm here to help!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "getting_started" }
            ]
        },
        getting_started_account: {
            message: "Creating Your Account 📝\n\n📋 Steps:\n1. Go to Sign Up page\n2. Enter your 10-digit mobile number\n3. Create a strong password (min 6 characters)\n4. Enter your tuition name\n5. Click 'Create Account'\n\n💡 Your mobile number is your login ID!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "getting_started" }
            ]
        },
        getting_started_student: {
            message: "Adding Your First Student 👥\n\n📋 Steps:\n1. Go to 'Students' tab\n2. Click 'Add New Student'\n3. Fill in: Name, Phone, Batch (required)\n4. Optional: Address, School, Class\n5. Click 'Add Student'\n\n💡 Students get auto-generated passwords!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "getting_started" }
            ]
        },
        getting_started_batch: {
            message: "Creating Your First Batch 📚\n\n📋 Steps:\n1. Go to 'Batches' tab\n2. Click 'Create New Batch'\n3. Enter batch name (e.g., 'Class 10 Science')\n4. Add description (optional)\n5. Click 'Create Batch'\n\n💡 You can create multiple batches for different classes!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "getting_started" }
            ]
        },
        getting_started_attendance: {
            message: "Marking Your First Attendance ✅\n\n📋 Steps:\n1. Go to 'Attendance' tab\n2. Select date (or use today)\n3. Click Present/Absent/Late for each student\n4. Click 'Save Attendance'\n\n💡 Students will get notified automatically!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "getting_started" }
            ]
        },
        getting_started_navigation: {
            message: "Basic Navigation 🧭\n\n📋 Main Tabs:\n• Dashboard - Overview of everything\n• Students - Manage your students\n• Batches - Organize classes\n• Attendance - Mark daily attendance\n• Homework - Share assignments\n• Reports - View analytics\n• Profile - Your settings\n\n💡 Use the bottom navigation to switch tabs!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "getting_started" }
            ]
        },
        troubleshooting: {
            message: "Troubleshooting 🔧\n\nHaving issues? Let me help you fix them!",
            options: [
                { text: "Login problems", action: "troubleshooting_login" },
                { text: "App not working", action: "troubleshooting_app" },
                { text: "Data not saving", action: "troubleshooting_data" },
                { text: "Slow performance", action: "troubleshooting_slow" },
                { text: "Notification issues", action: "troubleshooting_notifications" },
                { text: "🔙 Back", action: "main" }
            ]
        },
        troubleshooting_login: {
            message: "Login Problems 🔐\n\nCommon issues:\n\n❌ Can't login:\n• Check mobile number (10 digits)\n• Verify password is correct\n• Make sure you're using the right login page\n\n❌ Forgot password:\n• Contact your tutor (for students)\n• Use account recovery (for tutors)\n\n❌ Account locked:\n• Wait 15 minutes and try again\n• Contact support if persists",
            options: [
                { text: "Still need help", action: "contact" },
                { text: "🔙 Back", action: "troubleshooting" }
            ]
        },
        troubleshooting_app: {
            message: "App Not Working 🛠️\n\nTry these fixes:\n\n1. Refresh the page (F5 or pull down)\n2. Clear browser cache\n3. Check internet connection\n4. Try a different browser\n5. Restart your device\n\n💡 If still not working, contact support!",
            options: [
                { text: "Still need help", action: "contact" },
                { text: "🔙 Back", action: "troubleshooting" }
            ]
        },
        troubleshooting_data: {
            message: "Data Not Saving 💾\n\nIf data isn't saving:\n\n1. Check internet connection\n2. Make sure all required fields are filled\n3. Try refreshing and saving again\n4. Check if you're logged in\n5. Clear browser cache\n\n💡 Always see a success message after saving!",
            options: [
                { text: "Still need help", action: "contact" },
                { text: "🔙 Back", action: "troubleshooting" }
            ]
        },
        troubleshooting_slow: {
            message: "Slow Performance 🐌\n\nTo speed things up:\n\n1. Close other browser tabs\n2. Clear browser cache\n3. Check internet speed\n4. Restart your device\n5. Update your browser\n\n💡 The app works best on modern browsers!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "troubleshooting" }
            ]
        },
        troubleshooting_notifications: {
            message: "Notification Issues 🔔\n\nIf notifications aren't working:\n\n1. Check browser notification permission\n2. Make sure notifications are enabled\n3. Check if browser supports push notifications\n4. Try on a different device\n5. Clear browser cache\n\n💡 Notifications work best on Chrome/Firefox!",
            options: [
                { text: "Still need help", action: "contact" },
                { text: "🔙 Back", action: "troubleshooting" }
            ]
        },
        account: {
            message: "Account & Security 👤\n\nManage your account and keep it secure!",
            options: [
                { text: "Account management", action: "account_management" },
                { text: "Change profile", action: "account_profile" },
                { text: "Security & Privacy", action: "account_security" },
                { text: "Data backup", action: "account_backup" },
                { text: "🔙 Back", action: "main" }
            ]
        },
        account_management: {
            message: "Account Management 📋\n\nYou can:\n• View your profile\n• Update tuition name\n• Change tutor name\n• Update address\n• View mobile number\n\n⚠️ Mobile number cannot be changed for security!\n\n💡 Go to Profile tab to manage your account!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "account" }
            ]
        },
        account_profile: {
            message: "Updating Your Profile ✏️\n\n📋 Steps:\n1. Go to 'Profile' tab\n2. Click 'Edit Profile'\n3. Update any information\n4. Click 'Save Changes'\n\nYou can update:\n• Tuition name\n• Tutor/owner name\n• Address\n\n💡 Changes are saved immediately!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "account" }
            ]
        },
        account_security: {
            message: "Security & Privacy 🔒\n\nYour data is safe with us!\n\n✅ Secure login (password protected)\n✅ Data encrypted in database\n✅ Only you can see your data\n✅ No sharing with third parties\n\n💡 Always log out when using shared devices!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "account" }
            ]
        },
        account_backup: {
            message: "Data Backup 💾\n\nYour data is automatically saved:\n\n✅ All data stored securely\n✅ Automatic backups\n✅ No manual backup needed\n\n💡 Your data is safe even if you clear browser cache!\n\n⚠️ To export data, contact support!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "account" }
            ]
        },
        student_portal: {
            message: "Student Portal Help 🎓\n\nEverything about the student login!",
            options: [
                { text: "Student login", action: "student_portal_login" },
                { text: "Student features", action: "student_portal_features" },
                { text: "View attendance", action: "student_portal_attendance" },
                { text: "Check homework", action: "student_portal_homework" },
                { text: "Contact teacher", action: "student_portal_contact" },
                { text: "🔙 Back", action: "main" }
            ]
        },
        student_portal_login: {
            message: "Student Login 🔐\n\n📋 How to login:\n\n1. Go to Student Login page\n2. Enter your phone number (registered with tutor)\n3. Enter your password\n4. Click 'Login'\n\n❌ Forgot password?\n• Contact your tutor for password reset\n• They can generate a new password\n\n💡 Your tutor provides the login credentials!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "Still need help", action: "contact" },
                { text: "🔙 Back", action: "student_portal" }
            ]
        },
        student_portal_features: {
            message: "Student Portal Features 🎯\n\nAs a student, you can:\n\n✅ View your attendance (monthly grid)\n✅ Check all homework assignments\n✅ See batch details\n✅ View your profile\n✅ Contact teacher information\n\n💡 Everything you need in one place!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "student_portal" }
            ]
        },
        student_portal_attendance: {
            message: "Viewing Your Attendance 📊\n\n📋 Steps:\n1. Login to student portal\n2. Go to 'Attendance' tab\n3. See your monthly attendance grid\n\nColor indicators:\n🟢 Green = Present\n🔴 Red = Absent\n🟡 Yellow = Late\n\n💡 Attendance is updated by your tutor!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "student_portal" }
            ]
        },
        student_portal_homework: {
            message: "Checking Your Homework 📝\n\n📋 Steps:\n1. Login to student portal\n2. Go to 'Homework' tab\n3. See all assigned homework\n4. Check due dates\n5. View homework details and files\n\n💡 You'll get notifications when new homework is shared!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "student_portal" }
            ]
        },
        student_portal_contact: {
            message: "Contacting Your Teacher 📞\n\n📋 How to contact:\n\n1. Login to student portal\n2. Go to 'Profile' tab\n3. Scroll to 'About Tuition' section\n4. See teacher contact information:\n   • Tuition name\n   • Teacher name\n   • Address\n   • Phone number\n\n💡 Use this info to reach out to your teacher!",
            options: [
                { text: "Got it! 👍", action: "main" },
                { text: "🔙 Back", action: "student_portal" }
            ]
        }
    },

    // Current state
    currentAction: 'main',
    history: [],
    
    // Get content based on user role
    get content() {
        return this.userRole === 'student' ? this.contentStudent : this.contentTutor;
    },

    // Initialize the bot
    init: function() {
        console.log('Niya: init() called, userRole=', this.userRole);
        this.createBotUI();
        this.attachEventListeners();
        this.showWelcomePopup();
        console.log('Niya: Initialization complete');
    },

    // Create bot UI elements
    createBotUI: function() {
        // Check if button already exists
        if (document.getElementById('niya-help-button')) {
            console.log('Niya: Button already exists, skipping creation');
            return;
        }
        
        console.log('Niya: Creating floating button...');
        // Create floating button
        const button = document.createElement('div');
        button.id = 'niya-help-button';
        button.innerHTML = `
            <img src="/static/niya_avatar_50x50.png" alt="Niya" class="niya-avatar" onerror="console.error('Niya: Image failed to load:', this.src); this.style.backgroundColor='#4F46E5'; this.style.display='flex'; this.style.alignItems='center'; this.style.justifyContent='center'; this.innerHTML='😊';">
            <div class="niya-pulse"></div>
        `;
        button.setAttribute('aria-label', 'Open Niya Help Bot');
        
        if (!document.body) {
            console.error('Niya: document.body is not available!');
            return;
        }
        
        // Force inline styles to ensure visibility
        button.style.cssText = `
            position: fixed !important;
            bottom: 100px !important;
            right: 20px !important;
            width: 60px !important;
            height: 60px !important;
            background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
            border-radius: 50% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            cursor: pointer !important;
            box-shadow: 0 4px 20px rgba(79, 70, 229, 0.4) !important;
            z-index: 99999 !important;
            visibility: visible !important;
            opacity: 1 !important;
        `;
        
        document.body.appendChild(button);
        console.log('Niya: Floating button created and appended to body');
        console.log('Niya: Button element:', button);
        console.log('Niya: Button exists in DOM:', !!document.getElementById('niya-help-button'));
        
        // Check computed styles after a delay
        setTimeout(() => {
            const btn = document.getElementById('niya-help-button');
            if (btn) {
                const styles = window.getComputedStyle(btn);
                const rect = btn.getBoundingClientRect();
                console.log('Niya: Button display:', styles.display);
                console.log('Niya: Button visibility:', styles.visibility);
                console.log('Niya: Button opacity:', styles.opacity);
                console.log('Niya: Button z-index:', styles.zIndex);
                console.log('Niya: Button position:', rect);
                console.log('Niya: Button is visible:', rect.width > 0 && rect.height > 0);
                
                if (rect.width === 0 || rect.height === 0) {
                    console.error('Niya: Button has zero dimensions!');
                }
            } else {
                console.error('Niya: Button not found in DOM!');
            }
        }, 200);

        // Create bot panel
        const panel = document.createElement('div');
        panel.id = 'niya-help-panel';
        panel.innerHTML = `
            <div class="niya-header">
                <div class="niya-header-content">
                    <div class="niya-avatar-container">
                        <img src="/static/niya_avatar_80x80.png" alt="Niya" class="niya-avatar-large">
                        <span class="niya-status-dot"></span>
                    </div>
                    <div>
                        <div class="niya-name">Niya</div>
                        <div class="niya-status">Always here to help!</div>
                    </div>
                </div>
                <button class="niya-close" aria-label="Close help bot">✕</button>
            </div>
            <div class="niya-messages" id="niya-messages"></div>
            <div class="niya-options" id="niya-options"></div>
        `;
        document.body.appendChild(panel);

        // Load initial message
        this.showMessage('main');
    },

    // Attach event listeners
    attachEventListeners: function() {
        const button = document.getElementById('niya-help-button');
        const panel = document.getElementById('niya-help-panel');
        const closeBtn = panel.querySelector('.niya-close');

        button.addEventListener('click', () => this.togglePanel());
        closeBtn.addEventListener('click', () => this.closePanel());
        
        // Close on outside click
        panel.addEventListener('click', (e) => {
            if (e.target === panel) {
                this.closePanel();
            }
        });
    },

    // Toggle panel (automatically fullscreen)
    togglePanel: function() {
        const panel = document.getElementById('niya-help-panel');
        const isOpen = panel.classList.contains('niya-open');
        
        if (!isOpen) {
            // Opening - check if this is a fresh start or reopening
            const messagesDiv = document.getElementById('niya-messages');
            const isFreshStart = !messagesDiv || messagesDiv.children.length === 0;
            
            // Reset to main
            this.currentAction = 'main';
            this.history = ['main'];
            
            // Open panel first
            panel.classList.add('niya-open');
            panel.classList.add('niya-fullscreen'); // Automatically fullscreen
            
            // Wait for panel animation to complete, then show message
            setTimeout(() => {
                if (isFreshStart) {
                    // First time opening - show welcome message
                    this.showMessage('main');
                } else {
                    // Reopening - show "hello again" message
                    const welcomeAgainEl = document.createElement('div');
                    welcomeAgainEl.className = 'niya-message niya-message-left';
                    welcomeAgainEl.innerHTML = `
                        <div class="niya-message-avatar">
                            <img src="/static/niya_avatar_50x50.png" alt="Niya">
                        </div>
                        <div class="niya-message-content">
                            Hello again! How can I help you? 😊
                        </div>
                    `;
                    messagesDiv.appendChild(welcomeAgainEl);
                    // Show options
                    this.showOptionsOnly('main');
                }
                
                // Scroll to top when opening
                if (messagesDiv) {
                    messagesDiv.scrollTop = 0;
                }
            }, 400); // Wait for panel open animation (0.4s)
        } else {
            this.closePanel();
        }
    },

    // Close panel and clear chat
    closePanel: function() {
        const panel = document.getElementById('niya-help-panel');
        const messagesDiv = document.getElementById('niya-messages');
        
        // Clear all messages
        if (messagesDiv) {
            messagesDiv.innerHTML = '';
        }
        
        // Reset state
        this.currentAction = 'main';
        this.history = [];
        
        // Close panel
        panel.classList.remove('niya-open');
        panel.classList.remove('niya-fullscreen'); // Remove fullscreen when closing
    },

    // Show message and options (chat-like interface)
    showMessage: function(action) {
        const content = this.content[action];
        if (!content) return;

        this.currentAction = action;
        
        // Only add to history if not going back
        if (action !== 'main' || this.history.length === 0) {
            this.history.push(action);
        }

        const messagesDiv = document.getElementById('niya-messages');
        const optionsDiv = document.getElementById('niya-options');

        // Add Niya's message (left side)
        const messageEl = document.createElement('div');
        messageEl.className = 'niya-message niya-message-left';
        messageEl.innerHTML = `
            <div class="niya-message-avatar">
                <img src="/static/niya_avatar_50x50.png" alt="Niya">
            </div>
            <div class="niya-message-content">
                ${content.message.replace(/\n/g, '<br>')}
            </div>
        `;
        messagesDiv.appendChild(messageEl);
        // Don't auto-scroll to bottom - keep at current position or top

        // Clear options section (keep it hidden but don't remove for layout)
        optionsDiv.innerHTML = '';

        // Add options as clickable chat options in the messages area
        setTimeout(() => {
            content.options.forEach((option, index) => {
                const optionEl = document.createElement('div');
                optionEl.className = 'niya-message niya-message-option';
                optionEl.style.opacity = '0';
                optionEl.style.transform = 'translateY(5px)';
                optionEl.innerHTML = `
                    <div class="niya-option-content">
                        ${option.text}
                    </div>
                `;
                
                // Stagger animation for smoother appearance using requestAnimationFrame
                const animateIn = () => {
                    requestAnimationFrame(() => {
                        optionEl.style.transition = 'opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1), transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
                        optionEl.style.opacity = '1';
                        optionEl.style.transform = 'translateY(0)';
                    });
                };
                setTimeout(animateIn, index * 40); // 40ms delay between each option for smoother stagger
                
                optionEl.addEventListener('click', () => {
                    // Remove all option messages
                    const allOptions = messagesDiv.querySelectorAll('.niya-message-option');
                    allOptions.forEach(opt => opt.remove());

                // Show user's selected option as a message (right side)
                const userMessageEl = document.createElement('div');
                userMessageEl.className = 'niya-message niya-message-right';
                userMessageEl.innerHTML = `
                    <div class="niya-message-content">
                        ${option.text}
                    </div>
                    <div class="niya-message-avatar">
                        <div class="niya-user-avatar">👤</div>
                    </div>
                `;
                messagesDiv.appendChild(userMessageEl);
                // Keep scroll at top - don't auto-scroll

                    // Then show Niya's response
                    setTimeout(() => {
                        if (option.action === 'close') {
                            // Show closing message before closing
                            const closingMessage = document.createElement('div');
                            closingMessage.className = 'niya-message niya-message-left';
                            closingMessage.innerHTML = `
                                <div class="niya-message-avatar">
                                    <img src="/static/niya_avatar_50x50.png" alt="Niya">
                                </div>
                                <div class="niya-message-content">
                                    Thanks for chatting! Feel free to come back anytime if you need help! 😊
                                </div>
                            `;
                            messagesDiv.appendChild(closingMessage);
                            setTimeout(() => {
                                this.closePanel();
                            }, 1000);
                        } else if (option.action === 'main') {
                            // Show back to main message
                            const backMessage = document.createElement('div');
                            backMessage.className = 'niya-message niya-message-left';
                            backMessage.innerHTML = `
                                <div class="niya-message-avatar">
                                    <img src="/static/niya_avatar_50x50.png" alt="Niya">
                                </div>
                                <div class="niya-message-content">
                                    Sure! Let's go back to the main menu. What else can I help you with? 😊
                                </div>
                            `;
                            messagesDiv.appendChild(backMessage);
                            setTimeout(() => {
                                // Reset to main but don't show the initial message again
                                this.currentAction = 'main';
                                this.history = ['main'];
                                // Just show options, not the message
                                this.showOptionsOnly('main');
                            }, 500);
                        } else {
                            this.showMessage(option.action);
                        }
                    }, 300);
                });
                messagesDiv.appendChild(optionEl);
                // Keep scroll at top - don't auto-scroll to bottom
            });
        }, 200);
    },

    // Show only options without message (for back to main)
    showOptionsOnly: function(action) {
        const content = this.content[action];
        if (!content) return;

        const messagesDiv = document.getElementById('niya-messages');
        const optionsDiv = document.getElementById('niya-options');

        // Clear options section
        optionsDiv.innerHTML = '';

        // Add options as clickable chat options in the messages area
        setTimeout(() => {
            content.options.forEach((option, index) => {
                const optionEl = document.createElement('div');
                optionEl.className = 'niya-message niya-message-option';
                optionEl.style.opacity = '0';
                optionEl.style.transform = 'translateY(5px)';
                optionEl.innerHTML = `
                    <div class="niya-option-content">
                        ${option.text}
                    </div>
                `;
                
                // Stagger animation for smoother appearance using requestAnimationFrame
                const animateIn = () => {
                    requestAnimationFrame(() => {
                        optionEl.style.transition = 'opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1), transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
                        optionEl.style.opacity = '1';
                        optionEl.style.transform = 'translateY(0)';
                    });
                };
                setTimeout(animateIn, index * 40); // 40ms delay between each option for smoother stagger
                
                optionEl.addEventListener('click', () => {
                    // Remove all option messages
                    const allOptions = messagesDiv.querySelectorAll('.niya-message-option');
                    allOptions.forEach(opt => opt.remove());

                    // Show user's selected option as a message (right side)
                    const userMessageEl = document.createElement('div');
                    userMessageEl.className = 'niya-message niya-message-right';
                    userMessageEl.innerHTML = `
                        <div class="niya-message-content">
                            ${option.text}
                        </div>
                        <div class="niya-message-avatar">
                            <div class="niya-user-avatar">👤</div>
                        </div>
                    `;
                    messagesDiv.appendChild(userMessageEl);
                    // Keep scroll at top - don't auto-scroll

                    // Then show Niya's response
                    setTimeout(() => {
                        if (option.action === 'close') {
                            const closingMessage = document.createElement('div');
                            closingMessage.className = 'niya-message niya-message-left';
                            closingMessage.innerHTML = `
                                <div class="niya-message-avatar">
                                    <img src="/static/niya_avatar_50x50.png" alt="Niya">
                                </div>
                                <div class="niya-message-content">
                                    Thanks for chatting! Feel free to come back anytime if you need help! 😊
                                </div>
                            `;
                            messagesDiv.appendChild(closingMessage);
                            setTimeout(() => {
                                this.closePanel();
                            }, 1000);
                        } else if (option.action === 'main') {
                            const backMessage = document.createElement('div');
                            backMessage.className = 'niya-message niya-message-left';
                            backMessage.innerHTML = `
                                <div class="niya-message-avatar">
                                    <img src="/static/niya_avatar_50x50.png" alt="Niya">
                                </div>
                                <div class="niya-message-content">
                                    Sure! Let's go back to the main menu. What else can I help you with? 😊
                                </div>
                            `;
                            messagesDiv.appendChild(backMessage);
                            setTimeout(() => {
                                this.currentAction = 'main';
                                this.history = ['main'];
                                this.showOptionsOnly('main');
                            }, 500);
                        } else {
                            this.showMessage(option.action);
                        }
                    }, 300);
                });
                messagesDiv.appendChild(optionEl);
                // Keep scroll at top - don't auto-scroll to bottom
            });
        }, 200);
    },

    // Show welcome popup
    showWelcomePopup: function() {
        const hasSeenWelcome = sessionStorage.getItem('niya_welcome_seen');
        if (hasSeenWelcome) return;

        setTimeout(() => {
            const button = document.getElementById('niya-help-button');
            if (!button) return;

            const popup = document.createElement('div');
            popup.id = 'niya-welcome-popup';
            popup.className = 'niya-welcome-popup';
            popup.innerHTML = `
                <button class="niya-popup-close" aria-label="Close">✕</button>
                <div class="niya-popup-content">
                    <img src="/static/niya_avatar_100x100.png" alt="Niya" class="niya-popup-avatar">
                    <p>Hi! I'm <strong>Niya</strong> 😊</p>
                    <p>I'm here to help you with TuitionTrack!</p>
                    <p>Click me anytime if you need assistance!</p>
                </div>
            `;
            document.body.appendChild(popup);

            // Show popup with animation
            setTimeout(() => popup.classList.add('show'), 100);

            // Close handlers
            popup.querySelector('.niya-popup-close').addEventListener('click', () => {
                popup.classList.remove('show');
                setTimeout(() => popup.remove(), 300);
                sessionStorage.setItem('niya_welcome_seen', 'true');
            });

            // Auto-close after 8 seconds
            setTimeout(() => {
                if (popup.parentNode) {
                    popup.classList.remove('show');
                    setTimeout(() => popup.remove(), 300);
                    sessionStorage.setItem('niya_welcome_seen', 'true');
                }
            }, 8000);
        }, 2000);
    }
};

// Initialize when DOM is ready - only if user is logged in
document.addEventListener('DOMContentLoaded', () => {
    console.log('Niya: DOMContentLoaded fired');
    console.log('Niya: window.userLoggedIn =', typeof window.userLoggedIn !== 'undefined' ? window.userLoggedIn : 'undefined');
    console.log('Niya: window.userRole =', typeof window.userRole !== 'undefined' ? window.userRole : 'undefined');
    console.log('Niya: document.body exists:', !!document.body);
    
    // Since the template only loads this script when logged in, always initialize
    // Determine if user is tutor or student
    const isStudent = window.location.pathname.includes('/student/') ||
                     (typeof window.userRole !== 'undefined' && window.userRole === 'student') ||
                     document.querySelector('.student-header');
    
    NiyaHelpBot.userRole = isStudent ? 'student' : 'tutor';
    console.log('Niya: Initializing help bot for role:', NiyaHelpBot.userRole);
    
    // Small delay to ensure body is ready
    setTimeout(() => {
        try {
            NiyaHelpBot.init();
        } catch (error) {
            console.error('Niya: Error during initialization:', error);
        }
    }, 100);
});

