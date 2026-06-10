# 🔍 Hệ Thống Phát Hiện Dị Thường Đánh Giá Amazon

Ứng dụng web sử dụng **Streamlit** để phát hiện đánh giá đáng ngờ trên Amazon Beauty reviews bằng mô hình hybrid học máy và phân tích đồ thị.

---

## 📋 Yêu Cầu Hệ Thống

- **Python:** 3.9+
- **OS:** macOS / Linux / Windows
- **RAM:** 8GB (khuyến nghị 16GB)

---

## 🚀 Cách Cài Đặt & Chạy Ứng Dụng

### 1. Kích Hoạt Virtual Environment

```bash
cd "/Users/mac/Downloads/MXH FINAL"
source venv/bin/activate
```

**Output mong đợi:** Dòng lệnh sẽ có prefix `(venv)`
```
(venv) mac@MacBookPro MXH FINAL %
```

### 2. Cài Đặt Dependencies (Nếu Cần)

```bash
pip install -r requirements.txt
```

### 3. Chạy Ứng Dụng Streamlit

```bash
streamlit run frontend.py
```

**Output mong đợi:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501

  Hint: press 'q' to quit
```

Ứng dụng sẽ tự động mở ở trình duyệt. Nếu không, vào: **http://localhost:8501**

---

## 📊 Dữ Liệu Hệ Thống

- **Tổng Users:** 588,332
- **Tổng Reviews:** 644,689
- **Tổng Products:** 108,784
- **Tổng Edges:** 2,201,904

---

## 🔎 Hướng Dẫn Truy Vấn Dữ Liệu

Ứng dụng hỗ trợ 2 loại truy vấn chính:

### A. Truy Vấn Theo User ID (Tìm đánh giá của 1 user)

#### Định Dạng User ID:
- **Độ dài:** 30 ký tự
- **Ký tự:** Chữ in hoa (A-Z) + Số (0-9)
- **Ví dụ:** `AED2GFGIAJ22PHMZGSKH2CPUF75Q`

#### Cách Nhập:
1. Mở tab **"🔍 Tìm kiếm theo User"** trong ứng dụng
2. Nhập User ID vào ô input: `AED2GFGIAJ22PHMZGSKH2CPUF75Q`
3. Nhấn **Enter** hoặc click nút **Search**
4. Kết quả hiển thị:
   - Số đánh giá của user
   - Điểm dị thường trung bình
   - Danh sách chi tiết các đánh giá

#### Ví Dụ User ID Hợp Lệ:
```
AED2GFGIAJ22PHMZGSKH2CPUF75Q
AH54X3UMWTAMUJU2CVWYWNZVETLA
AGAXSRTPVGYIV36UQ3T4K7Q7DJFQ
AGJYFSGSS22LIDYSMYTIMBLV7M6Q
AELHNTAU54MHMZWHKPD3DNMJJRRA
```

---

### B. Truy Vấn Theo Product ID (Tìm đánh giá của 1 sản phẩm)

#### Định Dạng Product ID:
- **Độ dài:** 10 ký tự
- **Ký tự:** Chữ in hoa (A-Z) + Số (0-9)
- **Tiền tố:** Thường là `B` + 9 ký tự
- **Ví dụ:** `B000050FDE`

#### Cách Nhập:
1. Mở tab **"🔍 Tìm kiếm theo Product"** trong ứng dụng
2. Nhập Product ID vào ô input: `B000050FDE`
3. Nhấn **Enter** hoặc click nút **Search**
4. Kết quả hiển thị:
   - Số đánh giá của sản phẩm
   - Tỷ lệ đánh giá đáng ngờ
   - Danh sách chi tiết các đánh giá (User, Rating, Helpful votes, Verified)

#### Ví Dụ Product ID Hợp Lệ:
```
B000050FDE (190 reviews)
B0000151RX
B000J6H60U
B00005H0A0
B0000BVBV2
```

---

## 📈 Thông Tin Hiển Thị Trong Kết Quả

### Khi Tìm Kiếm User:
| Trường | Ý Nghĩa |
|-------|--------|
| **User ID** | ID người dùng |
| **Tổng Reviews** | Số đánh giá của user |
| **Avg Anomaly Score** | Điểm dị thường trung bình (0-1) |
| **Avg Graph Suspicion** | Điểm đáng ngờ đồ thị trung bình |
| **Hybrid Anomaly Score** | Điểm hybrid dị thường |
| **Graph Suspicion** | Điểm đáng ngờ từ phân tích đồ thị |

### Khi Tìm Kiếm Product:
| Trường | Ý Nghĩa |
|-------|--------|
| **Product ID** | ID sản phẩm |
| **Tổng Reviews** | Số đánh giá cho sản phẩm |
| **Risky Reviews** | Số đánh giá được đánh dấu là có rủi ro |
| **Avg Anomaly Score** | Điểm dị thường trung bình |
| **Rating** | Xếp hạng sao (2-5) |
| **Helpful Votes** | Số lượt "hữu ích" |
| **Verified Purchase** | Có phải mua xác minh hay không |

---

## 🛑 Xử Lý Lỗi Thường Gặp

### ❌ Lỗi: "Không tìm thấy kết quả cho ID: ..."

**Nguyên nhân:** ID không tồn tại trong hệ thống

**Giải pháp:**
1. Kiểm tra lại độ dài ID (User: 30 ký tự, Product: 10 ký tự)
2. Kiểm tra chính tả (có khoảng trắng, ký tự đặc biệt không?)
3. Sử dụng ví dụ ID từ danh sách trên
4. Thử với các ID mẫu khác

### ❌ Lỗi: "KeyError: 'num_users'"

**Nguyên nhân:** Cache Streamlit cũ

**Giải pháp:**
1. Nhấn `C` trong terminal chạy Streamlit để xóa cache
2. Hoặc dừng ứng dụng (Ctrl+C) rồi chạy lại:
   ```bash
   streamlit run frontend.py
   ```

### ❌ Lỗi: "Kết nối backend thất bại"

**Nguyên nhân:** backend.py không chạy được

**Giải pháp:**
1. Kiểm tra file dữ liệu:
   ```bash
   ls data/gold/All_Beauty/
   ```
   Phải có: `nodes_review.parquet`, `edges_*.parquet`, `hybrid_model/metadata.json`

2. Chạy test backend:
   ```bash
   python backend.py
   ```

---

## 💻 Cấu Trúc Dự Án

```
MXH FINAL/
├── frontend.py              # Ứng dụng Streamlit (UI)
├── backend.py               # Engine xử lý dữ liệu
├── README.md                # Hướng dẫn này
├── requirements.txt         # Dependencies
├── data/
│   └── gold/All_Beauty/     # Dữ liệu chính
│       ├── nodes_review.parquet
│       ├── edges_*.parquet
│       └── hybrid_model/
│           ├── metadata.json
│           └── combined_features.npy
└── venv/                    # Virtual environment
```

---

## 🔧 Lệnh Hữu Ích

### Kiểm Tra Dữ Liệu Có Sẵn Không

```bash
# Kiểm tra file parquet
python -c "import pandas as pd; print(pd.read_parquet('data/gold/All_Beauty/nodes_review.parquet').shape)"

# Kiểm tra metadata
python -c "import json; print(json.load(open('data/gold/All_Beauty/hybrid_model/metadata.json')))"
```

### Tìm User/Product ID Mẫu

```bash
python << 'EOF'
import pandas as pd

# Lấy 5 User ID đầu tiên
reviews = pd.read_parquet('data/gold/All_Beauty/nodes_review.parquet')
print("User IDs mẫu:")
print(reviews['user_id'].unique()[:5])

# Lấy 5 Product ID đầu tiên
edges = pd.read_parquet('data/gold/All_Beauty/edges_review_item.parquet')
print("\nProduct IDs mẫu:")
print(edges['dst'].unique()[:5])
EOF
```

---

## 📞 Liên Hệ & Hỗ Trợ

- **Dữ liệu:** Amazon Reviews 2023 (McAuley Lab)
- **Framework:** Streamlit + Pandas + NumPy
- **Mô hình:** Hybrid Neural Network + Graph Analysis

---

## 📝 Ghi Chú

- Các truy vấn có thể mất vài giây nếu sản phẩm có nhiều đánh giá (>100)
- Điểm dị thường (0-1): Cao hơn = Đáng ngờ hơn
- Tất cả ID phải nhập đúng chính xác, không có khoảng trắng

---

**Phiên bản:** 1.0 | **Cập nhật:** 2024
