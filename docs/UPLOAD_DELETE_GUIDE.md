# 📤 Upload & 🗑️ Delete Functionality Guide

## 📤 Upload Flow

### **1. Access Upload Page**

- **Home Page** → Click "📤 Upload Your First Book" button
- **Library Page** → Click "📤 Upload Your First Book" button
- **Sidebar** → Click "📤 Upload" navigation
- **Quick Actions** → Click "📤 Upload New Book" in sidebar

### **2. Upload Interface**

```
┌─────────────────────────────────────┐
│ 📤 Upload Books                     │
├─────────────────────────────────────┤
│ ┌─────────────────────────────────┐ │
│ │ 📁 Drag & Drop PDF Files Here  │ │
│ │ Or click to browse and select  │ │
│ └─────────────────────────────────┘ │
│                                     │
│ 📋 Selected Files                   │
│ ┌─────────┬─────────┬─────────────┐│
│ │ Name    │ Size    │ Type        ││
│ ├─────────┼─────────┼─────────────┤│
│ │ book.pdf│ 1.2MB   │ application ││
│ └─────────┴─────────┴─────────────┘│
│                                     │
│ 🚀 Process Files                   │
└─────────────────────────────────────┘
```

### **3. Upload Process**

1. **Select Files** - Choose one or more PDF files
2. **Review Details** - See file names, sizes, and types
3. **Process Files** - Click "🚀 Process Files" button
4. **Processing** - Files are:
   - Saved to `uploads/` directory
   - Text extracted using PyMuPDF
   - Chunked and embedded using sentence transformers
   - Stored in Chroma vector database
   - Metadata saved to SQLite database
5. **Success** - Redirected to Library page

### **4. Upload Features**

- ✅ **Multiple files** - Upload several PDFs at once
- ✅ **Drag & drop** - Modern file selection interface
- ✅ **File validation** - Only PDF files accepted
- ✅ **Progress feedback** - Processing status shown
- ✅ **Error handling** - Clear error messages
- ✅ **File size limits** - Up to 100MB per file

## 🗑️ Delete Functionality

### **1. Delete from Library**

- **Location**: Library page book cards
- **Button**: "🗑️ Delete" button on each book card
- **Confirmation**: Two-step confirmation process

### **2. Delete from Book Settings**

- **Location**: Book interface → Settings tab
- **Button**: "🗑️ Delete Book" button
- **Confirmation**: Two-step confirmation process

### **3. Delete Process**

```
Step 1: Click Delete Button
    ↓
Step 2: Confirmation Warning
    ↓
Step 3: Click Delete Again
    ↓
Step 4: Complete Deletion
```

### **4. What Gets Deleted**

- ✅ **Database records** - Book metadata, chat history, summaries
- ✅ **PDF files** - Physical files from `uploads/` directory
- ✅ **Vector stores** - Chroma collections from `chroma_db/`
- ✅ **Session state** - Current book selection cleared if needed

### **5. Delete Safety Features**

- **Confirmation dialog** - Prevents accidental deletions
- **Two-step process** - Must click delete twice
- **Warning messages** - Clear indication of what will be deleted
- **Error handling** - Graceful handling of file system errors

## 🔄 Complete Upload & Delete Flow

### **Upload Flow**

```
User → Upload Page → Select Files → Process → Library → Success
```

### **Delete Flow**

```
User → Library/Settings → Click Delete → Confirm → Delete → Success
```

## 📁 File Management

### **Upload Directory Structure**

```
uploads/
├── uuid_book1.pdf
├── uuid_book2.pdf
└── uuid_book3.pdf

chroma_db/
├── book_uuid1/
├── book_uuid2/
└── book_uuid3/

books.db (SQLite)
├── books table
├── chat_history table
└── summaries table
```

### **File Naming Convention**

- **PDF files**: `{uuid}_{original_filename}.pdf`
- **Vector collections**: `book_{uuid}`
- **Database IDs**: Auto-incrementing integers

## 🎯 Key Features

### **Upload Features**

- **Multiple file support** - Upload several PDFs simultaneously
- **Progress tracking** - Real-time processing feedback
- **Error recovery** - Graceful handling of processing errors
- **File validation** - Automatic PDF format checking
- **Size optimization** - Efficient file storage

### **Delete Features**

- **Complete cleanup** - Removes all associated data
- **Safe deletion** - Confirmation prevents accidents
- **File system cleanup** - Removes physical files and directories
- **Database cleanup** - Removes all related records
- **State management** - Updates UI state appropriately

## ⚠️ Important Notes

### **Upload Limitations**

- **File format**: PDF files only
- **File size**: Up to 100MB per file
- **Processing time**: Depends on file size and content
- **Text extraction**: Works best with searchable PDFs

### **Delete Warnings**

- **Permanent deletion** - Cannot be undone
- **Complete removal** - All data and files deleted
- **No recovery** - No backup or restore functionality
- **Cascade deletion** - Removes chat history and summaries

## 🚀 Best Practices

### **For Uploads**

1. **Use searchable PDFs** for best text extraction
2. **Keep files under 100MB** for faster processing
3. **Upload multiple files** to batch process
4. **Check file names** before uploading

### **For Deletions**

1. **Confirm carefully** before deleting
2. **Backup important data** if needed
3. **Check book selection** before deleting
4. **Use settings page** for detailed book management

## 🔧 Technical Implementation

### **Upload Process**

```python
def process_uploaded_files(uploaded_files):
    for file in uploaded_files:
        # Save file with UUID
        file_id = str(uuid.uuid4())
        file_path = f"uploads/{file_id}_{filename}"

        # Extract text
        pages = extract_text_from_pdf(file_path)

        # Create vector store
        vector_store = chunk_and_embed(pages, collection_name=f"book_{file_id}")

        # Save to database
        book_id = db.add_book(title, filename, file_path, collection_name)
```

### **Delete Process**

```python
def delete_book(book_id):
    # Get book info
    book_info = get_book_by_id(book_id)

    # Delete database records
    delete_chat_history(book_id)
    delete_summaries(book_id)
    delete_book_record(book_id)

    # Delete physical files
    os.remove(book_info.file_path)
    shutil.rmtree(f"chroma_db/{book_info.collection_name}")
```

## 🎉 Summary

The upload and delete functionality provides:

- **Easy file upload** with drag-and-drop interface
- **Safe file deletion** with confirmation dialogs
- **Complete data management** - uploads, processes, and deletes all associated data
- **User-friendly interface** with clear feedback and error handling
- **Robust file system** management with proper cleanup

Users can confidently upload their PDFs and manage their library with full control over their data! 📚✨
