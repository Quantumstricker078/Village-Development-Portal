# 🌱 Village Development Information Portal

> A web-based information system designed to **digitize village-level governance and services**, developed as part of the **BCA curriculum**.

---

## 📌 Project Snapshot

🎓 **Course:** Bachelor of Computer Applications (BCA)  
🛠️ **Type:** Academic Web Application  
🌍 **Domain:** E-Governance / Rural Development  
⚙️ **Stack:** Flask • SQLite • HTML • CSS • Bootstrap  

---

## 🌟 Why This Project?

Many villages still rely on **manual notice boards, paper records, and word-of-mouth communication**, which leads to:
- ❌ Poor awareness of government schemes  
- ❌ Inefficient service access  
- ❌ Manual errors and delays  

✅ This portal solves that by providing a **single digital platform** for all village-related information.

---

## 🎯 Objectives

- Centralize village-level information  
- Improve transparency and accessibility  
- Digitally manage beneficiaries  
- Reduce manual workload  
- Promote digital inclusion  

---

## 👥 System Users

### 🧑 Villagers
- View schemes, services, and notices  
- Search for relevant information  

### 👨‍💼 Admin
- Secure login  
- Manage schemes & notices  
- Register and track beneficiaries  

---

## ⭐ Key Features

- 📋 Government Schemes Directory  
- 🏛️ Local Services Information  
- 📢 Village Notices & Announcements  
- 👥 Beneficiary Management  
- 🔍 Search Functionality  
- 🔐 Admin Dashboard  
- 📱 Responsive UI  

---

## 🧩 System Architecture (Illustration)

+---------+ +-----------+ +------------+
| User | ---> | Frontend | ---> | Backend |
| /Admin | | (UI) | | (Flask) |
+---------+ +-----------+ +------------+
|
v
+------------+
| SQLite DB |
+------------+


---

## 🛠️ Technology Stack

### 🎨 Frontend
- HTML5  
- CSS3  
- Bootstrap 5  
- JavaScript  

### ⚙️ Backend
- Python  
- Flask Framework  

### 🗄️ Database
- SQLite3  

### 🧰 Tools
- VS Code  
- Git & GitHub  

---

## 🗄️ Database Design (ERD – Overview)

**Main Entities:**
- Users  
- Schemes  
- Services  
- Notices  
- Beneficiaries  

📌 Relationships ensure **data consistency and integrity**.

---

## 🔄 Data Flow Diagram (DFD – Level 0)

User/Admin
|
v
Village Development Portal
|
v
Database


---

## 🎨 UI Design & Wireframes

Wireframes were created to plan:
- 🧭 Navigation flow  
- 🧩 Page layout  
- 😊 User experience  

📄 Key Pages:
- Home  
- Schemes  
- Notices  
- Admin Dashboard  

---

## 🔐 Security Highlights

- Admin authentication  
- Hashed passwords  
- Parameterized SQL queries  
- Restricted admin access  

---

## ⚙️ Installation & Setup

### 📋 Prerequisites
- Python 3.x  
- Git  

### 📥 Clone the Repository
```bash
git clone https://github.com/your-username/Village-Development-Portal.git
cd Village-Development-Portal

▶️ Run the Application

pip install -r requirements.txt
python app.py

🌐 Open in browser:

http://localhost:5000

🧪 Testing

    Manual testing

    Form validation testing

    UI responsiveness testing

    Admin workflow testing

✅ All modules tested successfully.
⚠️ Limitations

    SQLite (local database)

    No real-time notifications

    Single admin role

🚀 Future Enhancements

    📱 Mobile App

    🌐 Multilingual Support

    📩 SMS / Email Notifications

    📊 Analytics Dashboard

🔁 Version Control

    Git for source control

    GitHub for code hosting

    Commit-based change tracking

🎓 Academic Declaration

This project is developed strictly for academic purposes as part of the BCA curriculum, demonstrating practical application of web development concepts.
✅ Conclusion

The Village Development Information Portal is a step toward digital village governance, offering a simple, scalable, and transparent solution for rural information management.

⭐ If you find this project useful, consider starring the repository!