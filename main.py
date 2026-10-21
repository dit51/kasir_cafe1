import os
import streamlit as st
from streamlit_option_menu import option_menu
st.set_page_config(page_title='Kasir', layout='wide')

PPN = 0.10

MENU = [
    {'id': 1, 'nama': 'Amerikano',      'harga': 20000, 'jenis': 'Minuman', 'kategori': 'Coffee',         'gambar': 'gambar/amerikano.png'},
    {'id': 2, 'nama': 'Latte',          'harga': 25000, 'jenis': 'Minuman', 'kategori': 'Coffee',         'gambar': 'gambar/latte.png'},
    {'id': 3, 'nama': 'Matcha',      'harga': 18000, 'jenis': 'Minuman', 'kategori': 'Non-coffee',     'gambar': 'gambar/matcha.png'},
    {'id': 4, 'nama': 'Kentang Goreng', 'harga': 15000, 'jenis': 'Makanan', 'kategori': 'Makanan Ringan', 'gambar': 'gambar/kentang.png'},
]

KATEGORI = {
    'Minuman' : ['Semua', 'Coffee', 'Non-coffee'],
    'Makanan' : ['Semua', 'Makanan Berat', 'Makanan Ringan']
}

if 'cart' not in st.session_state:
    st.session_state.cart = {}

if 'uang' not in st.session_state:
    st.session_state.uang = 0

def rupiah(angka):
    return f'{angka:,.0f}'.replace(',','.')

def cari_menu(item_id):
    for m in MENU:
        if m['id'] == item_id:
            return m

def tambah(item_id):
    st.session_state.cart[item_id] = st.session_state.cart.get(item_id, 0) + 1

def kurang(item_id):
    if item_id not in st.session_state.cart:
        return
    st.session_state.cart[item_id] -= 1
    if st.session_state.cart[item_id] <= 0:
        del st.session_state.cart[item_id]

def kosongkan():
    st.session_state.cart = {}
    st.session_state.uang = 0
 
def bayar():
    cart = st.session_state.cart
    total = sum(cari_menu(i)['harga'] * q for i, q in cart.items()) * (1 + PPN)

    if not cart:
        st.session_state.pesan = ('warning', 'Keranjang masih kosong🙄')
    elif st.session_state.uang < total:
        st.session_state.pesan = ('error', 'Uang nya kurang🤬')
    else:
        kembalian = st.session_state.uang - total
        st.session_state.pesan = ('success', f'Pemabayaran Berhasil🤑 kembalian Rp {rupiah(kembalian)}')
        st.session_state.cart = {}
        st.session_state.uang = 0
        st.snow()

with st.sidebar :
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if os.path.exists('logo telkom.png'):
            st.image('logo telkom.png')
        st.title('Our Menu')

        jenis = st.segmented_control('Jenis', ['Minuman', 'Makanan'],)
        if jenis:
            kategori = st.selectbox(f'Kategori {jenis}', KATEGORI[jenis])
        else:
            kategori = 'Semua'

tampil = []
for m in MENU:
    cocok_jenis = jenis is None or m ['jenis'] == jenis
    cocok_kategori = kategori == 'Semua' or m['kategori'] == kategori
    if cocok_jenis and cocok_kategori:
        tampil.append(m)

kiri, kanan = st.columns([2.2, 1], gap='large')

with kiri:
    if jenis is None:
        st.header('Semua Menu')
    elif kategori == 'Semua':
        st.header(jenis)
    else:
        st.header(f'{jenis} - {kategori}')

    if not tampil:
        st.info('Maaf belum ada menu di kategori ini')

    cols = st.columns(3)
    for i, m in enumerate(tampil):
        with cols[i % 3]:
            with st.container(border=True):
                if os.path.exists(m['gambar']):
                    st.image(m['gambar'], use_container_width=True)
                else:
                    st.markdown(
                                "<div style='background:#eef2f6;border-radius:8px;height:120px;"
                                "display:flex;align-items:center;justify-content:center;"
                                "color:#999;font-size:.85rem;'>Belum ada gambar</div>",
                                unsafe_allow_html=True,
                            )
                st.markdown(f"**{m['nama']}**")
                st.caption(f"Rp {rupiah(m['harga'])}")
                qty = st.session_state.cart.get(m['id'], 0)
                st.button(
                    'Tambah',                      
                    key=f"add_{m['id']}",
                    on_click=tambah,
                    args=(m['id'],),
                    use_container_width=True,
                )
                if qty:
                    st.caption(f"Di keranjang: {qty}")

with kanan:
    subtotal = sum(cari_menu(i)['harga'] * q for i, q in st.session_state.cart.items())
    pajak = subtotal * PPN
    total = subtotal + pajak

    with st.container(border=True):
        st.subheader('Pembayaran')

        if 'pesan' in st.session_state:
            tipe, teks = st.session_state.pop('pesan')
            getattr(st, tipe)(teks)

        if not st.session_state.cart:
            st.caption('Belum ada pesanan. ')

        for item_id, qty in list(st.session_state.cart.items()):
            m = cari_menu(item_id)
            a, b, c = st.columns([3, 1, 1])
            a.markdown(f"**{m['nama']}**  \n{qty} x {rupiah(m['harga'])} = {rupiah(m['harga'] * qty)}")
            b.button('➖', key=f"min_{item_id}", on_click=kurang, args=(item_id,))
            c.button('➕', key=f"plus_{item_id}", on_click=tambah, args=(item_id,))

        st.divider()
        st.write(f"Subtotal: Rp {rupiah(subtotal)}")
        st.write(f"PPN 10%: Rp {rupiah(pajak)}")
        st.markdown(f"### Total: Rp {rupiah(total)}")

        st.number_input('Uang diterima', min_value=0, step=5000, key='uang')
        if st.session_state.cart and st.session_state.uang >= total:
            st.write(f'Kembalian: Rp {rupiah(st.session_state.uang - total)}')

        c1, c2 = st.columns([1, 2])
        c1.button('Clear', on_click=kosongkan, use_container_width=True)
        c2.button('Bayar', type='primary', on_click=bayar, use_container_width=True)