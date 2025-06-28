# 🩸 Streamlit Frontend for Blood Test Analyzer

A minimal, user-friendly web interface for the Blood Test Analyzer API.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install streamlit requests
```

### 2. Start Backend (Required)
```bash
# Make sure the FastAPI backend is running first
python main.py
```

### 3. Start Streamlit Frontend
```bash
# Option 1: Using the helper script (recommended)
python run_streamlit.py

# Option 2: Direct streamlit command
streamlit run streamlit_app.py
```

### 4. Open Browser
- Streamlit will automatically open: `http://localhost:8501`
- Backend API should be running on: `http://localhost:8000`

## 📱 Features

### 📄 File Analysis Tab
- **Upload PDF**: Drag & drop blood test reports (max 10MB)
- **Custom Query**: Describe what analysis you want
- **Real-time Processing**: See progress with spinner
- **Formatted Results**: Professional medical analysis display

### 💬 Text Analysis Tab  
- **No File Needed**: Ask questions without uploading
- **Medical Insights**: Get information about blood tests
- **Educational Content**: Learn about health markers

### 📊 Sidebar Features
- **System Status**: Real-time API health monitoring
- **Recent Analyses**: Quick view of last 3 analyses
- **Statistics**: Total analyses, queue status

## 🎨 Interface Highlights

- **Clean Design**: Professional medical interface
- **Real-time Status**: Live connection monitoring
- **Responsive Layout**: Works on desktop and mobile
- **Progress Indicators**: Clear feedback during processing
- **Error Handling**: User-friendly error messages
- **Medical Formatting**: Properly structured analysis results

## 🔧 Technical Details

- **Frontend**: Streamlit (Python web framework)
- **Backend Communication**: RESTful API calls via requests
- **File Handling**: Secure PDF upload with validation
- **Styling**: Medical-themed UI with appropriate colors
- **Error Handling**: Comprehensive try-catch blocks

## 📚 API Endpoints Used

- `GET /health` - System health check
- `POST /analyze` - File-based blood test analysis  
- `POST /analyze-text` - Text-only queries
- `GET /analyses/recent` - Recent analysis history

## 🛠️ Troubleshooting

**❌ "API is not responding"**
- Ensure FastAPI backend is running: `python main.py`
- Check if port 8000 is available
- Verify backend health: `curl http://localhost:8000/health`

**📱 Streamlit won't start**
- Install Streamlit: `pip install streamlit`
- Use the helper script: `python run_streamlit.py`
- Check port 8501 is available

**📁 File upload issues**
- Ensure PDF format (max 10MB)
- Check file isn't corrupted
- Try with sample files from `/data` folder

## 💡 Usage Tips

1. **Start Backend First**: Always ensure the FastAPI server is running before launching Streamlit
2. **Use Sample Files**: Test with files in the `/data` directory
3. **Custom Queries**: Be specific about what analysis you want
4. **Monitor Sidebar**: Check system status and recent analyses
5. **Mobile Friendly**: Interface works well on phones/tablets

---

*This Streamlit frontend provides a clean, professional interface for the Blood Test Analyzer while keeping the code minimal and leveraging the existing FastAPI backend.* 