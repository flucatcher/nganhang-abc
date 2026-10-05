# === PHẦN 1: THƯ VIỆN & XÂY DỰNG LỚP ĐỐI TƯỢNG (OOP) ===
import streamlit as st
import datetime
import random
import pandas as pd

# ---------------------------------------------------------
# LỚP ĐỐI TƯỢNG: TaiKhoan
# Ý nghĩa: Đóng gói (Encapsulation) dữ liệu và phương thức xử lý của từng khách hàng.
# ---------------------------------------------------------
class TaiKhoan:
    def __init__(self, stk, ten, pin, so_tien_ban_dau):
        self.stk = stk
        self.ten = ten
        self.pin = pin
        self.so_du = so_tien_ban_dau
        
        # Cấu trúc dữ liệu List (Danh sách): Dùng để lưu trữ chuỗi lịch sử giao dịch.
        # Mỗi phần tử là một dictionary nhỏ để lát nữa dễ dàng chuyển thành Bảng (DataFrame) hiển thị.
        self.lich_su = []
        self.ghi_lich_su("Nhận tiền", "Mở tài khoản hệ thống", so_tien_ban_dau)

    def ghi_lich_su(self, loai_gd, chi_tiet, so_tien):
        # Hàm thêm giao dịch vào List với độ phức tạp thời gian O(1)
        thoi_gian = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        giao_dich = {
            "Thời gian": thoi_gian,
            "Loại giao dịch": loai_gd,
            "Chi tiết": chi_tiet,
            "Biến động (VND)": f"+{so_tien:,.0f}" if loai_gd == "Nhận tiền" else f"-{so_tien:,.0f}",
            "Số dư cuối (VND)": f"{self.so_du:,.0f}"
        }
        self.lich_su.append(giao_dich)

    def nap_tien(self, so_tien):
        # Kiểm tra tính hợp lệ bằng rẽ nhánh if-else
        if so_tien > 0: 
            self.so_du += so_tien
            self.ghi_lich_su("Nhận tiền", "Nạp tiền tại quầy", so_tien)
            return True, f"Giao dịch thành công. Số dư hiện tại: {self.so_du:,.0f} VND."
        return False, "Giao dịch không hợp lệ: Số tiền nạp phải lớn hơn 0 VND."

    def rut_tien(self, so_tien, pin_nhap):
        # Xác thực và bắt lỗi logic
        if pin_nhap != self.pin:
            return False, "Xác thực thất bại: Mã PIN không chính xác."
        if so_tien <= 0:
            return False, "Giao dịch không hợp lệ: Số tiền rút phải lớn hơn 0 VND."
        if so_tien > self.so_du:
            return False, f"Giao dịch thất bại: Số dư không khả dụng. (Hiện tại: {self.so_du:,.0f} VND)"

        self.so_du -= so_tien
        self.ghi_lich_su("Trừ tiền", "Rút tiền mặt", so_tien)
        return True, f"Giao dịch thành công. Số dư hiện tại: {self.so_du:,.0f} VND."

    def chuyen_khoan(self, tk_dich, so_tien, pin_nhap):
        # tk_dich là đối tượng nhận tiền. Giao tiếp giữa 2 đối tượng độc lập.
        if pin_nhap != self.pin:
            return False, "Xác thực thất bại: Mã PIN không chính xác."
        if so_tien <= 0:
            return False, "Giao dịch không hợp lệ: Số tiền chuyển phải lớn hơn 0 VND."
        if so_tien > self.so_du:
            return False, "Giao dịch thất bại: Số dư tài khoản không đủ để thực hiện."

        # Trừ tiền tài khoản nguồn
        self.so_du -= so_tien
        self.ghi_lich_su("Trừ tiền", f"Chuyển khoản đến STK {tk_dich.stk}", so_tien)

        # Cộng tiền tài khoản đích
        tk_dich.so_du += so_tien
        tk_dich.ghi_lich_su("Nhận tiền", f"Nhận chuyển khoản từ STK {self.stk}", so_tien)

        return True, f"Chuyển khoản thành công. Số dư hiện tại: {self.so_du:,.0f} VND."
# === PHẦN 2: KHỞI TẠO BẢNG BĂM (HASH TABLE) & MENU ĐIỀU HƯỚNG ===

# Cấu hình trang với layout mở rộng (wide) để có không gian chia cột
st.set_page_config(page_title="Ngân hàng ABC", page_icon="🏦", layout="wide")

# --- BƠM CSS TÙY CHỈNH GIAO DIỆN (UI BOTOX) ---
st.markdown("""
<style>
    /* 1. Lột xác menu Radio bên trái thành dạng Button */
    div.stRadio > div[role="radiogroup"] > label {
        background-color: #233130; /* Màu nền xám xanh sang trọng */
        padding: 12px 15px;
        border-radius: 8px;
        margin-bottom: 8px;
        transition: all 0.3s ease-in-out;
        border: 1px solid rgba(255, 255, 255, 0.1);
        cursor: pointer;
    }
    div.stRadio > div[role="radiogroup"] > label:hover {
        background-color: #3a4f4e; /* Sáng lên nhẹ khi di chuột */
        transform: translateY(-2px); /* Hiệu ứng nảy lên */
        border: 1px solid #B3F05D;
    }
    /* Giấu cái chấm tròn mặc định của Radio đi */
    div.stRadio > div[role="radiogroup"] > label > div:first-child {
        display: none;
    }
    /* Chỉnh chữ menu to và nét hơn */
    div.stRadio > div[role="radiogroup"] > label p {
        font-size: 16px;
        font-weight: 600;
    }

    /* 2. Tiêu đề Sidebar to & ngầu hơn */
    [data-testid="stSidebar"] h2 {
        font-size: 26px !important;
        font-weight: 800 !important;
        color: #B3F05D !important; /* Xanh neon */
    }

    /* 3. Lột xác Nút bấm chính (Primary Button) */
    button[kind="primary"] {
        background-color: #B3F05D !important;
        color: #192625 !important; /* Chữ đen trên nền xanh */
        font-weight: 800 !important;
        font-size: 16px !important;
        border-radius: 8px !important;
        padding: 24px !important; /* Cho nút to ra */
        border: none !important;
        transition: all 0.2s;
    }
    button[kind="primary"]:hover {
        background-color: #C4F575 !important; /* Xanh chói hơn khi hover */
        transform: scale(1.02);
    }

    /* 4. Lột xác Ô nhập liệu (Input Field) */
    /* Chỉnh viền input sang màu Xanh Neon cực nổi bật */
    .stTextInput > div > div > input {
        background-color: #192625 !important; /* Nền đen/xám đậm */
        color: white !important; /* Chữ trắng cho dễ đọc */
        border: 2px solid #B3F05D !important; /* Viền xanh neon */
        border-radius: 8px;
        padding: 10px 12px;
    }
    /* Focus vào ô nào thì viền sáng lên rực rỡ */
    .stTextInput > div > div > input:focus {
        border-color: #ffff00 !important; /* Viền vàng chói */
        box-shadow: 0 0 10px rgba(255, 255, 0, 0.4);
    }

    /* 5. Lột xác Thẻ (Card) chứa thông tin */
    /* Tạo hiệu ứng "thẻ nổi" */
    div.stMetric {
        background-color: #233130; /* Nền xám xanh */
        padding: 15px 20px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 10px;
    }
    /* Chỉnh số tiền lớn (Big Number) màu vàng neon cho dễ thấy */
    div.stMetric > div:first-child {
        color: #B3F05D !important; 
        font-size: 2.5rem !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)
# ----------------------------------------------

# 1. Khởi tạo Cơ sở dữ liệu (Bảng băm - Hash Table)
# Áp dụng Dictionary để lưu trữ và truy xuất các đối tượng TaiKhoan với độ phức tạp thời gian O(1).
if 'kho_data' not in st.session_state:
    st.session_state.kho_data = {}

db = st.session_state.kho_data # Biến tham chiếu (Alias) cho ngắn gọn

def phat_sinh_stk():
    # Vòng lặp phát sinh số tài khoản ngẫu nhiên đảm bảo tính duy nhất
    while True:
        so = "0111" + str(random.randint(10000, 99999))
        # Toán tử 'not in' kiểm tra sự tồn tại của khóa (key) trong Bảng băm cực kỳ tối ưu
        if so not in db:
            return so

# 2. Xây dựng Thanh điều hướng bên trái (Sidebar)
with st.sidebar:
    st.markdown("## 🏦 NGÂN HÀNG ABC")
    st.markdown("---")
    menu = ["Mở tài khoản", "Nạp tiền", "Rút tiền", "Chuyển khoản", "Tra cứu & Sao kê"]
    # Thay selectbox bằng radio button để giao diện nhìn thoáng và trực quan hơn
    lua_chon = st.radio("Vui lòng chọn nghiệp vụ:", menu)
    st.markdown("---")
    st.info("🔹 Hệ thống quản trị lõi (Core Banking)\n\n🔹 Cấu trúc: OOP & Hash Table")

# Hiển thị tiêu đề động dựa trên nghiệp vụ đang chọn
st.markdown(f"<h2 style='color: #1E3A8A;'>Nghiệp vụ: {lua_chon.upper()}</h2>", unsafe_allow_html=True)
st.markdown("---")


# === PHẦN 3.1: XỬ LÝ GIAO DIỆN MỞ TÀI KHOẢN & NẠP TIỀN ===

if lua_chon == "Mở tài khoản":
    st.markdown("#### Điền thông tin đăng ký tài khoản mới")
    
    # Sử dụng container và chia cột để UI gọn gàng, hiện đại
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            ten = st.text_input("Họ và tên khách hàng:")
            pin = st.text_input("Thiết lập mã PIN (Gồm 4-6 chữ số):", type="password")
            
        with col2:
            so_tien = st.number_input("Số tiền gửi ban đầu tối thiểu (VND):", min_value=0, step=50000)
            st.markdown("<br>", unsafe_allow_html=True) # Khoảng trống ép nút bấm xuống ngang hàng với ô input
            btn_mo_tk = st.button("Xác nhận đăng ký", use_container_width=True)
    
    if btn_mo_tk:
        # Kiểm tra dữ liệu đầu vào (Data Validation)
        if so_tien >= 50000 and ten.strip() and pin.strip():
            stk_moi = phat_sinh_stk()
            
            # Khởi tạo đối tượng mới và lưu vào Bảng băm
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
        
    if st.button("Thực hiện nạp tiền"):
        # Tra cứu Key trên Hash Table với O(1)
        if stk in db:
            # Gọi phương thức của đối tượng để xử lý nghiệp vụ
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
            # Truyền tham số số tiền và mã PIN vào phương thức của đối tượng để xử lý
            thanh_cong, thong_bao = db[stk].rut_tien(int(tien), pin)
            if thanh_cong:
                st.success(f"✅ {thong_bao}")
            else:
                st.error(f"❌ {thong_bao}")
        else:
            st.error("❌ Giao dịch thất bại: Số tài khoản không tồn tại trên hệ thống.")

elif lua_chon == "Chuyển khoản":
    st.markdown("#### Chuyển khoản nội bộ hệ thống ABC")
    
    # Chia 2 cột: Cột trái cho Người gửi, Cột phải cho Người nhận & Số tiền
    col_nguon, col_dich = st.columns(2)
    
    with col_nguon:
        st.markdown("##### 📤 Thông tin người gửi")
        stk_nguon = st.text_input("Số tài khoản trích tiền:")
        pin = st.text_input("Mã PIN xác thực:", type="password")
        
    with col_dich:
        st.markdown("##### 📥 Thông tin người nhận")
        stk_dich = st.text_input("Số tài khoản thụ hưởng:")
        tien = st.number_input("Số tiền chuyển (VND):", min_value=0, step=50000)
        
    if st.button("Xác nhận chuyển khoản", use_container_width=True):
        # Tra cứu đồng thời 2 tài khoản trên Bảng băm (Độ phức tạp O(1) cho mỗi lần tra cứu)
        if stk_nguon in db and stk_dich in db:
            if stk_nguon == stk_dich:
                st.error("❌ Giao dịch không hợp lệ: Không thể chuyển tiền đến chính tài khoản trích tiền.")
            else:
                # Giao tiếp giữa 2 Đối tượng (Object Interaction): 
                # Truyền đối tượng db[stk_dich] vào phương thức của db[stk_nguon]
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
        
    if st.button("Truy xuất dữ liệu"):
        if stk in db:
            tk = db[stk] # Lấy trực tiếp đối tượng tài khoản từ Hash Table
            if pin == tk.pin:
                st.success("✅ Xác thực thành công!")
                st.markdown(f"### 👤 Chủ tài khoản: **{tk.ten.upper()}**")
                st.markdown(f"### 💰 Số dư hiện tại: **{tk.so_du:,.0f} VND**")
                
                st.markdown("---")
                st.markdown("📜 **SỔ PHỤ NGÂN HÀNG (LỊCH SỬ GIAO DỊCH):**")
                
                # Chuyển đổi List (Mảng) chứa các Dictionary thành Pandas DataFrame để trực quan hóa dữ liệu
                df_sao_ke = pd.DataFrame(tk.lich_su)
                # Đánh lại số thứ tự (index) bắt đầu từ 1 thay vì 0 cho chuyên nghiệp
                df_sao_ke.index = df_sao_ke.index + 1 
                
                # Hiển thị bảng full màn hình với thư viện Streamlit
                st.dataframe(df_sao_ke, use_container_width=True)
            else:
                st.error("❌ Xác thực thất bại: Mã PIN không chính xác.")
        else:
            st.error("❌ Truy xuất thất bại: Số tài khoản không tồn tại trên hệ thống.")