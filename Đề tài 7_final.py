# THƯ VIỆN
from streamlit.proto import SelectWidgetFilterMode_pb2
import streamlit as st
import datetime
import random
import pandas as pd

class TaiKhoan: 
#Hàm ban đầu
    def __init__(self, stk, ten, pin, so_tien_ban_dau): 
        self.stk = stk                  # Số tài khoản
        self.ten = ten                  # Tên chủ tài khoản
        self.pin = pin                  # Mã PIN dùng để xác thực
        self.so_du = so_tien_ban_dau    # Số dư hiện khả dụng
        
        # Khởi tạo cấu trúc dữ liệu Danh sách (List) tuyến tính để lưu trữ lịch sử
        self.lich_su = [] 
        
        # Ghi lại giao dịch mở tài khoản
        self.ghi_lich_su("Nhận tiền", "Mở tài khoản hệ thống", so_tien_ban_dau) 

#Ghi lại lịch sử giao dịch
    def ghi_lich_su(self, loai_gd, chi_tiet, so_tien): 
        # Lấy thời gian thực của hệ thống
        thoi_gian = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
        
        # Đóng gói dữ liệu giao dịch vào cấu trúc Từ điển (Dictionary)
        # Giúp dễ dàng truy xuất các trường dữ liệu (Key-Value) khi xuất sao kê
        giao_dich = {
            "Thời gian": thoi_gian,
            "Loại giao dịch": loai_gd,
            "Chi tiết": chi_tiet,
            "Biến động (VND)": f"+{so_tien:,.0f}" if loai_gd == "Nhận tiền" else f"-{so_tien:,.0f}",
            "Số dư cuối (VND)": f"{self.so_du:,.0f}" 
        }
        # Thêm phần tử vào cuối danh sách (Độ phức tạp O(1) trung bình)
        self.lich_su.append(giao_dich) 

#Nạp tiền
    def nap_tien(self, so_tien):
        # Kiểm tra tính hợp lệ của dữ liệu đầu vào (Data Validation)
        if so_tien > 0:                             
            self.so_du += so_tien                   # Cập nhật trạng thái số dư
            self.ghi_lich_su("Nhận tiền", "Nạp tiền tại quầy", so_tien) 
            return True, f"Giao dịch thành công. Số dư hiện tại: {self.so_du:,.0f} VND." 
            
        return False, "Giao dịch không hợp lệ: Số tiền nạp phải lớn hơn 0 VND." 

#Rút tiền
    def rut_tien(self, so_tien, pin_nhap):
        han_muc_rut = 50000000                      # Ràng buộc nghiệp vụ: Hạn mức tối đa
        
        # Kiểm tra các điều kiện tiên quyết bằng chuỗi rẽ nhánh if
        if pin_nhap != self.pin:                    
            return False, "Xác thực thất bại: Mã PIN không chính xác."
        if so_tien <= 0:                            
            return False, "Giao dịch không hợp lệ: Số tiền rút phải lớn hơn 0 VND."
        if so_tien > han_muc_rut:                   
            return False, f"Giao dịch không hợp lệ: Hạn mức rút tiền tối đa là {han_muc_rut:,.0f} VND/lần!"
        if so_tien > self.so_du:                    
            return False, f"Giao dịch thất bại: Số dư không khả dụng. (Hiện tại: {self.so_du:,.0f} VND)"

        # Thực thi nghiệp vụ nếu thỏa mãn mọi điều kiện
        self.so_du -= so_tien                       
        self.ghi_lich_su("Trừ tiền", "Rút tiền mặt", so_tien) 
        return True, f"Giao dịch thành công. Số dư hiện tại: {self.so_du:,.0f} VND." 

#Chuyển khoản 
    def chuyen_khoan(self, tk_dich, so_tien, pin_nhap):
        han_muc_chuyen = 500000000                  # Ràng buộc nghiệp vụ: Hạn mức chuyển tối đa
        
        # Xác thực bảo mật và các ràng buộc dữ liệu
        if pin_nhap != self.pin:
            return False, "Xác thực thất bại: Mã PIN không chính xác."
        if self.stk == tk_dich.stk:                 
            return False, "Giao dịch không hợp lệ: Số tài khoản thụ hưởng trùng với tài khoản trích tiền."
        if so_tien <= 0:
            return False, "Giao dịch không hợp lệ: Số tiền chuyển phải lớn hơn 0 VND."
        if so_tien > han_muc_chuyen:
            return False, f"Giao dịch không hợp lệ: Hạn mức chuyển khoản tối đa là {han_muc_chuyen:,.0f} VND/lần!"
        if so_tien > self.so_du:
            return False, f"Giao dịch thất bại: Số dư không khả dụng. (Hiện tại: {self.so_du:,.0f} VND)"

        # Bước 1: Cập nhật trạng thái đối tượng nguồn (Trừ tiền và lưu lịch sử)
        self.so_du -= so_tien
        self.ghi_lich_su("Trừ tiền", f"Chuyển khoản đến STK {tk_dich.stk}", so_tien) 

        # Bước 2: Cập nhật trạng thái đối tượng đích thông qua tham chiếu (Cộng tiền và lưu lịch sử)
        tk_dich.so_du += so_tien
        tk_dich.ghi_lich_su("Nhận tiền", f"Nhận chuyển khoản từ STK {self.stk}", so_tien) 

        return True, f"Chuyển khoản thành công. Số dư hiện tại: {self.so_du:,.0f} VND."

# Cấu hình trang với layout mở rộng (wide) để có không gian chia cột
st.set_page_config(page_title="Ngân hàng ABC", page_icon="🏦", layout="wide")

# GIAO DIỆN SCANDINAVIAN MINIMALISM (ĐÃ TỐI ƯU UX/UI)
st.markdown("""
<style>
    /* 1. Nền tổng thể - Màu Birch White (Trắng bạch dương) ấm áp */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #f5f0eb !important;
    }

    /* 2. Text cơ bản - Nâng size và nét đậm hơn để dễ đọc */
    p, span, label, div {
        color: #3d3d3d !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-weight: 400 !important; /* Đã nâng độ đậm so với bản trước */
        font-size: 16px !important; /* Nâng size chữ chung */
    }

    /* FIX LỖI HIỂN THỊ CHỮ VISIBILITY & KEYBOARD - Trả lại font gốc cho Icon */
    span.material-symbols-rounded, 
    span.material-icons, 
    [data-testid="stIconMaterial"], 
    i {
        font-family: "Material Symbols Rounded", "Material Icons" !important;
        font-weight: normal !important;
    }

    /* 3. Tiêu đề các mục - In đậm, Up size */
    h1, h2, h3, h4, h5, h6 {
        color: #2b2b2b !important;
        font-weight: 700 !important; /* Ép in đậm tất cả tiêu đề */
        letter-spacing: 0.02em !important;
    }

    /* Tiêu đề Động (Nghiệp vụ: ...) to và rõ nét */
    h2 {
        font-size: 34px !important; 
        margin-bottom: 20px !important;
    }

    /* 4. Tiêu đề "NGÂN HÀNG ABC" - Điểm nhấn siêu to khổng lồ */
    [data-testid="stSidebar"] h2 {
        color: #3d3d3d !important; 
        font-size: 28px !important; /* Nâng size siêu to */
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        font-weight: 900 !important; /* Đậm nhất có thể */
        padding-bottom: 24px;
        border-bottom: 2px solid #d4cdc5;
        margin-bottom: 20px;
    }

    /* 5. Sidebar - Nền trắng kem mờ */
    [data-testid="stSidebar"] {
        background-color: #f0e9e1 !important;
        border-right: 1px solid rgba(212, 205, 197, 0.5) !important;
    }

    /* Menu Radio */
    div.stRadio > div[role="radiogroup"] > label {
        background-color: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 6px !important;
        padding: 12px 16px;
        margin-bottom: 8px;
        transition: all 0.3s ease-in-out !important;
    }
    /* Đổi màu hover menu sang Be đậm để không bị lệch tone */
    div.stRadio > div[role="radiogroup"] > label:hover {
        background-color: #e0d6cb !important; /* Màu be đậm */
        border: 1px solid #d4cdc5 !important;
    }
    div.stRadio > div[role="radiogroup"] > label > div:first-child { display: none; }
    div.stRadio > div[role="radiogroup"] > label p {
        font-size: 17px !important; /* Chữ menu to hơn */
        font-weight: 600 !important; /* In đậm menu */
        color: #3d3d3d !important;
    }

    /* 6. Nút bấm (Button) - Màu Pine Green làm chủ đạo, text trắng */
    button[kind="primary"], button[kind="secondary"] {
        background-color: #5a7a6b !important; /* Base xanh lá thông */
        color: #ffffff !important; /* Chữ trắng cực nổi */
        border-radius: 6px !important;
        border: none !important;
        padding: 14px 28px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 4px rgba(90, 122, 107, 0.2) !important;
    }
    /* Đưa chuột vào thì trầm xuống thành xanh đậm */
    button[kind="primary"]:hover, button[kind="secondary"]:hover {
        background-color: #445c50 !important; /* Xanh thông đậm */
        color: #ffffff !important;
        box-shadow: 0 4px 8px rgba(90, 122, 107, 0.3) !important;
        transform: translateY(-1px) !important;
    }
    button[kind="primary"]:active, button[kind="secondary"]:active {
        transform: scale(0.98) !important;
    }

    /* Ô nhập liệu (Input) - Nền trong suốt, viền rõ nét */
    .stTextInput > div > div > input, 
    .stNumberInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.3) !important;
        border: 1px solid #d4cdc5 !important;
        border-radius: 6px !important;
        padding: 12px 16px;
        color: #3d3d3d !important;
        font-size: 16px !important;
        transition: all 0.3s ease-in-out !important;
    }
    /* Focus: Viền xanh Pine Green */
    .stTextInput > div > div > input:focus, 
    .stNumberInput > div > div > input:focus {
        border-color: #5a7a6b !important; 
        box-shadow: 0 0 0 2px rgba(90, 122, 107, 0.2) !important; 
        background-color: rgba(255, 255, 255, 0.7) !important;
    }

    /* Thẻ Metric (Card Số dư) */
    div.stMetric {
        background-color: rgba(255, 255, 255, 0.6) !important; 
        border: 1px solid rgba(212, 205, 197, 0.4) !important;
        border-radius: 8px !important;
        padding: 24px !important;
    }
    div.stMetric > div:first-child {
        color: #2b2b2b !important; 
        font-size: 2.8rem !important; 
        font-weight: 700 !important; 
    }

    /* Thông báo lỗi/thành công */
    .stSuccess, .stError, .stInfo, .stWarning {
        background-color: rgba(255, 255, 255, 0.7) !important;
        border: 1px solid #d4cdc5 !important;
        border-radius: 6px !important;
        color: #3d3d3d !important;
        font-weight: 500 !important;
    }

    /* Khoảng không gian */
    .block-container {
        padding-top: 60px !important; 
        padding-bottom: 96px !important; 
        max-width: 950px !important; 
    }
    hr {
        border-top: 1px solid rgba(212, 205, 197, 0.5) !important;
        margin: 30px 0px !important;
    }
</style>
""", unsafe_allow_html=True)


# KHỞI TẠO CƠ SỞ DỮ LIỆU (Bảng băm - Hash Table)
if 'kho_data' not in st.session_state:
    st.session_state.kho_data = {}

db = st.session_state.kho_data

def phat_sinh_stk():
    chi_nhanh = "011"
    loai_the = "1"
    while True:
        ma_khach = str(random.randint(10000, 99999))
        stk_moi = chi_nhanh + loai_the + ma_khach
        if stk_moi not in db:
            return stk_moi


# THANH ĐIỀU HƯỚNG BÊN TRÁI (Sidebar)
with st.sidebar:
    st.markdown("## 🏦 NGÂN HÀNG ABC")
    menu = ["Mở tài khoản", "Nạp tiền", "Rút tiền", "Chuyển khoản", "Tra cứu & Sao kê"]
    lua_chon = st.radio("Vui lòng chọn nghiệp vụ:", menu)
    st.markdown("---")
    st.info("🔹 Hệ thống quản trị lõi (Core Banking)\n\n🔹 Cấu trúc: OOP & Hash Table")


# Hiển thị tiêu đề động dựa trên nghiệp vụ đang chọn
st.markdown(f"<h2>Nghiệp vụ: {lua_chon.upper()}</h2>", unsafe_allow_html=True)
st.markdown("---")


# XỬ LÝ GIAO DIỆN MỞ TÀI KHOẢN & NẠP TIỀN
if lua_chon == "Mở tài khoản":
    st.markdown("#### Điền thông tin đăng ký tài khoản mới")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            ten = st.text_input("Họ và tên khách hàng:")
            pin = st.text_input("Thiết lập mã PIN (Gồm 4-6 chữ số):", type="password")
            
        with col2:
            so_tien = st.number_input("Số tiền gửi ban đầu tối thiểu (VND):", min_value=0, step=50000)
            st.markdown("<br>", unsafe_allow_html=True)
            btn_mo_tk = st.button("Xác nhận đăng ký", use_container_width=True)
    
    if btn_mo_tk:
        if so_tien >= 50000 and ten.strip() and pin.strip():
            stk_moi = phat_sinh_stk()
            tai_khoan_moi = TaiKhoan(stk_moi, ten.strip(), pin.strip(), int(so_tien))
            db[stk_moi] = tai_khoan_moi
            
            st.success(f"✅ Giao dịch thành công. Kính chào Quý khách {ten.strip()}.")
            st.info(f"👉 SỐ TÀI KHOẢN ĐƯỢC CẤP CỦA QUÝ KHÁCH LÀ: **{stk_moi}** (Vui lòng bảo mật thông tin này!)")
        else:
            st.error("❌ Yêu cầu không hợp lệ: Vui lòng điền đầy đủ thông tin và nạp tối thiểu 50,000 VND.")

elif lua_chon == "Nạp tiền":
    st.markdown("#### Nộp tiền mặt vào tài khoản")
    
    col1, col2 = st.columns(2)
    with col1:
        stk = st.text_input("Nhập số tài khoản cần nạp:")
    with col2:
        tien = st.number_input("Số tiền nộp (VND):", min_value=0, step=50000)
        st.markdown("<br>", unsafe_allow_html=True)
        btn_nap = st.button("Thực hiện nạp tiền", use_container_width=True)
        
    if btn_nap:
        if stk in db:
            thanh_cong, thong_bao = db[stk].nap_tien(int(tien))
            if thanh_cong:
                st.success(f"✅ {thong_bao}")
            else:
                st.error(f"❌ {thong_bao}")
        else:
            st.error("❌ Giao dịch thất bại: Số tài khoản không tồn tại trên hệ thống.")

elif lua_chon == "Rút tiền":
    st.markdown("#### Rút tiền mặt từ tài khoản")
    
    col1, col2 = st.columns(2)
    with col1:
        stk = st.text_input("Nhập số tài khoản trích tiền:")
        pin = st.text_input("Nhập mã PIN xác thực:", type="password")
    with col2:
        tien = st.number_input("Số tiền yêu cầu rút (VND):", min_value=0, step=50000)
        st.markdown("<br>", unsafe_allow_html=True)
        btn_rut = st.button("Thực hiện rút tiền", use_container_width=True)
        
    if btn_rut:
        if stk in db:
            thanh_cong, thong_bao = db[stk].rut_tien(int(tien), pin)
            if thanh_cong:
                st.success(f"✅ {thong_bao}")
            else:
                st.error(f"❌ {thong_bao}")
        else:
            st.error("❌ Giao dịch thất bại: Số tài khoản không tồn tại trên hệ thống.")

elif lua_chon == "Chuyển khoản":
    st.markdown("#### Chuyển khoản nội bộ hệ thống ABC")
    
    col_nguon, col_dich = st.columns(2)
    
    with col_nguon:
        st.markdown("##### 📤 Thông tin người gửi")
        stk_nguon = st.text_input("Số tài khoản trích tiền:")
        pin = st.text_input("Mã PIN xác thực:", type="password")
        
    with col_dich:
        st.markdown("##### 📥 Thông tin người nhận")
        stk_dich = st.text_input("Số tài khoản thụ hưởng:")
        tien = st.number_input("Số tiền chuyển (VND):", min_value=0, step=50000)
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Xác nhận chuyển khoản", use_container_width=True):
        if stk_nguon in db and stk_dich in db:
            if stk_nguon == stk_dich:
                st.error("❌ Giao dịch không hợp lệ: Không thể chuyển tiền đến chính tài khoản trích tiền.")
            else:
                thanh_cong, thong_bao = db[stk_nguon].chuyen_khoan(db[stk_dich], int(tien), pin)
                if thanh_cong:
                    st.success(f"✅ {thong_bao}")
                else:
                    st.error(f"❌ {thong_bao}")
        else:
            st.error("❌ Giao dịch thất bại: Số tài khoản trích tiền hoặc thụ hưởng không hợp lệ.")

elif lua_chon == "Tra cứu & Sao kê":
    st.markdown("#### Truy vấn thông tin & Sao kê giao dịch")
    
    col1, col2 = st.columns(2)
    with col1:
        stk = st.text_input("Nhập số tài khoản cần tra cứu:")
    with col2:
        pin = st.text_input("Nhập mã PIN xác thực:", type="password")
        st.markdown("<br>", unsafe_allow_html=True)
        btn_tra_cuu = st.button("Truy xuất dữ liệu", use_container_width=True)
        
    if btn_tra_cuu:
        if stk in db:
            tk = db[stk] 
            if pin == tk.pin:
                st.success("✅ Xác thực thành công!")
                st.markdown(f"### 👤 Chủ tài khoản: **{tk.ten.upper()}**")
                st.markdown(f"### 💰 Số dư hiện tại: **{tk.so_du:,.0f} VND**")
                
                st.markdown("---")
                st.markdown("📜 **SỔ PHỤ NGÂN HÀNG (LỊCH SỬ GIAO DỊCH):**")
                
                df_sao_ke = pd.DataFrame(tk.lich_su)
                df_sao_ke.index = df_sao_ke.index + 1 
                st.dataframe(df_sao_ke, use_container_width=True)
            else:
                st.error("❌ Xác thực thất bại: Mã PIN không chính xác.")
        else:
            st.error("❌ Truy xuất thất bại: Số tài khoản không tồn tại trên hệ thống.")