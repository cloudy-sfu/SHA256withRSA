import dearpygui.dearpygui as dpg
from winapi import select_folder_spec, select_file_spec
from algorithms import generate, sign, verify, encrypt, decrypt
import ctypes
import os
import webbrowser
from pyperclip import copy, paste
import json

user32 = ctypes.windll.user32
w, h = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
dpg.create_context()

with dpg.font_registry():
    with dpg.font("SourceHanSansCN-Regular.otf", 16, tag="default_font"):
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
    dpg.bind_font("default_font")


def set_font_size():
    font_size = dpg.get_value("settings_font_size")
    dpg.set_global_font_scale(font_size)


def dpg_select_folder_wrapper(component):
    def dpg_select_folder():
        save_at = select_folder_spec()
        if not save_at:
            return
        dpg.set_value(component, save_at)

    return dpg_select_folder


def dpg_select_file_wrapper(component):
    def dpg_select_file():
        save_at = select_file_spec()
        if not save_at:
            return
        dpg.set_value(component, save_at)

    return dpg_select_file


def encrypt_select_file():
    save_at = select_file_spec()
    if not save_at:
        return
    dpg.set_value("encrypt_message", save_at)
    folder, filename = os.path.split(save_at)
    filename, extension = os.path.splitext(filename)
    encrypted_save_at = os.path.join(folder, f"{filename}_已加密.json")
    dpg.set_value("encrypt_save_at", encrypted_save_at)


def decrypt_select_file():
    save_at = select_file_spec()
    if not save_at:
        return
    dpg.set_value("decrypt_message", save_at)
    folder, filename = os.path.split(save_at)
    filename, extension = os.path.splitext(filename)
    if not filename.endswith("_已加密"):
        return
    filename = filename.removesuffix("_已加密")
    decrypted_save_at = os.path.join(folder, f"{filename}.txt")
    dpg.set_value("decrypt_save_at", decrypted_save_at)


def generate_gui():
    complexity = int(dpg.get_value("generate_complexity"))
    keys_name = dpg.get_value("generate_keys_name")
    generate_open = dpg.get_value("generate_open")
    save_at = dpg.get_value("generate_save_at")
    if not keys_name:
        dpg.set_value("message", "密钥名不能为空")
        dpg.show_item("banner")
        return
    if not (save_at and os.path.isdir(save_at)):
        dpg.set_value("message", "未指定保存密钥的文件夹位置")
        dpg.show_item("banner")
        return
    private_key, public_key = generate(complexity)
    with open(os.path.join(save_at, f"{keys_name}_私钥.txt"), "wb") as f:
        f.write(private_key)
    with open(os.path.join(save_at, f"{keys_name}_公钥.txt"), "wb") as f:
        f.write(public_key)
    if generate_open:
        webbrowser.open(save_at)
    else:
        dpg.set_value("message", "成功执行")
        dpg.show_item("banner")


def dpg_copy_wrapper(component):
    def dpg_copy():
        value = dpg.get_value(component)
        copy(value)
        dpg.set_value("message", f"成功复制了 {component} 栏目的值")
        dpg.show_item("banner")

    return dpg_copy


def dpg_paste_wrapper(component):
    def dpg_paste():
        dpg.set_value(component, paste())

    return dpg_paste


def sign_gui():
    message_fp = dpg.get_value("sign_message")
    if not (message_fp and os.path.isfile(message_fp)):
        dpg.set_value("message", "目标消息不存在")
        dpg.show_item("banner")
        return
    private_key_fp = dpg.get_value("sign_private_key")
    if not (private_key_fp and os.path.isfile(private_key_fp)):
        dpg.set_value("message", "私钥不存在")
        dpg.show_item("banner")
        return
    with open(message_fp, "rb") as f:
        message = f.read()
    with open(private_key_fp, "rb") as f:
        private_key = f.read()
    signature = sign(message, private_key)
    if signature:
        dpg.set_value("sign_signature", signature)
    else:
        dpg.set_value("message", "私钥格式不正确")
        dpg.show_item("banner")


def set_font_size_mouse(_, direction):
    if dpg.is_mouse_button_down(dpg.mvMouseButton_Middle):  # 0-Left, 1-Right, 2-Wheel
        dpg.set_value("settings_font_size", 1)
        dpg.set_global_font_scale(1)
    elif dpg.is_key_down(dpg.mvKey_Control):
        font_size = dpg.get_value("settings_font_size")
        font_size = round(max(0.1, font_size + 0.1 * direction), 1)
        dpg.set_value("settings_font_size", font_size)
        dpg.set_global_font_scale(font_size)


def verify_gui():
    message_fp = dpg.get_value("verify_message")
    if not (message_fp and os.path.isfile(message_fp)):
        dpg.set_value("message", "目标消息不存在")
        dpg.show_item("banner")
        return
    public_key_fp = dpg.get_value("verify_public_key")
    if not (public_key_fp and os.path.isfile(public_key_fp)):
        dpg.set_value("message", "公钥不存在")
        dpg.show_item("banner")
        return
    signature = dpg.get_value("verify_signature")
    if not signature:
        dpg.set_value("message", "签名为空")
        dpg.show_item("banner")
        return
    with open(message_fp, "rb") as f:
        message = f.read()
    with open(public_key_fp, "rb") as f:
        public_key = f.read()
    is_valid = verify(message, signature, public_key)
    if is_valid:
        dpg.set_value("message", "签名有效，在私钥持有者签署后，消息保持完整")
    else:
        dpg.set_value("message", "签名无效，在私钥持有者签署后，消息已被篡改")
    dpg.show_item("banner")


def encrypt_gui():
    message_fp = dpg.get_value("encrypt_message")
    if not (message_fp and os.path.isfile(message_fp)):
        dpg.set_value("message", "目标消息不存在")
        dpg.show_item("banner")
        return
    public_key_fp = dpg.get_value("encrypt_public_key")
    if not (public_key_fp and os.path.isfile(public_key_fp)):
        dpg.set_value("message", "公钥不存在")
        dpg.show_item("banner")
        return
    save_at = dpg.get_value("encrypt_save_at")
    with open(message_fp, "rb") as f:
        message = f.read()
    with open(public_key_fp, "rb") as f:
        public_key = f.read()
    encrypted = encrypt(message, public_key)
    if not encrypted:
        dpg.set_value("message", "公钥格式不正确")
        dpg.show_item("banner")
        return
    with open(save_at, "w") as f:
        json.dump(encrypted, f)
    if dpg.get_value("encrypt_open"):
        save_at_folder, _ = os.path.split(save_at)
        webbrowser.open(save_at_folder)
    else:
        dpg.set_value("message", "成功执行")
        dpg.show_item("banner")


def decrypt_gui():
    message_fp = dpg.get_value("decrypt_message")
    if not (message_fp and os.path.isfile(message_fp)):
        dpg.set_value("message", "目标消息不存在")
        dpg.show_item("banner")
        return
    private_key_fp = dpg.get_value("decrypt_private_key")
    if not (private_key_fp and os.path.isfile(private_key_fp)):
        dpg.set_value("message", "私钥不存在")
        dpg.show_item("banner")
        return
    with open(message_fp, "r") as f:
        message = json.load(f)
    with open(private_key_fp, "rb") as f:
        private_key = f.read()
    save_at = dpg.get_value("decrypt_save_at")
    decrypted_message = decrypt(message, private_key)
    if not decrypted_message:
        dpg.set_value("message", "私钥无法解密对应消息，消息或密钥至少其一、格式不正确。")
        dpg.show_item("banner")
        return
    with open(save_at, "wb") as f:
        f.write(decrypted_message)
    if dpg.get_value("decrypt_open"):
        save_at_folder, _ = os.path.split(save_at)
        webbrowser.open(save_at_folder)
    else:
        dpg.set_value("message", "成功执行")
        dpg.show_item("banner")


with dpg.window(tag="banner", pos=(int(0.05 * w), int(0.1 * h)), show=False,
                no_collapse=True, width=int(0.4 * w), height=int(0.2 * h),
                label="提示消息"):
    dpg.add_text(tag="message", wrap=0)

with dpg.window(tag="main_window"):
    with dpg.group():
        dpg.add_text("SHA256 with RSA")
        dpg.add_spacer(height=int(0.02 * h))

    with dpg.collapsing_header(label="设置"):
        dpg.add_input_float(format="%.1f", step=0.1, label="字体缩放比例", default_value=1.0,
                            tag="settings_font_size", callback=set_font_size)
        dpg.add_text("快捷键：按下“Ctrl”同时鼠标滚轮向上（放大字体）或向下（缩小字体）"
                     "滚动。按下鼠标滚轮，缩放比例重置为 1.",
                     wrap=0)
        dpg.add_spacer(height=int(0.02 * h))

    with dpg.collapsing_header(label="常见问题"):
        dpg.add_text("问题：程序界面上，文件、文件夹路径中存在问号。", wrap=0)
        dpg.add_text("解答：如果您看到问号，请不要惊慌。这是因为本软件的图形界面、使用了中文简体字符集。"
                     "不支持除简体中文、拉丁字母外的语言。如果您的文件路径包含其他字符，就会出现这个错误。然而，"
                     "错误只存在于屏幕显示时，所以这不会造成实际问题，您的文件将被正确保存在指定位置。",
                     wrap=0)
        dpg.add_spacer(height=int(0.02 * h))

    with dpg.collapsing_header(label="创建密钥"):
        dpg.add_text("创建一对新的 RSA 密钥，以 PEM 格式。", wrap=0)
        dpg.add_spacer(height=int(0.02 * h))
        dpg.add_combo(items=('1024', '2048', '4096'), label='复杂度',
                      default_value='2048', tag='generate_complexity')
        dpg.add_input_text(label="密钥文件名", default_value="通用RSA",
                           tag='generate_keys_name')
        dpg.add_text("创建后，密钥保存于：", wrap=0)
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag="generate_save_at", readonly=True)
            dpg.add_button(label="选择文件夹",
                           callback=dpg_select_folder_wrapper("generate_save_at"))
        dpg.add_checkbox(label="在创建密钥后打开保存密钥的文件夹", default_value=True,
                         tag="generate_open")
        dpg.add_button(label='创建', callback=generate_gui)
        dpg.add_spacer(height=int(0.02 * h))

    with dpg.collapsing_header(label="来源验证：签署（使用私钥）"):
        dpg.add_text("签署消息，向所有人证明你是消息的发送者。", wrap=0)
        dpg.add_spacer(height=int(0.02 * h))
        dpg.add_text("选择目标消息（文本文件）", wrap=0)
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag="sign_message", readonly=True)
            dpg.add_button(label="目标消息",
                           callback=dpg_select_file_wrapper("sign_message"))
        dpg.add_text("选择私钥", wrap=0)
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag="sign_private_key", readonly=True)
            dpg.add_button(label="私钥",
                           callback=dpg_select_file_wrapper("sign_private_key"))
        dpg.add_button(label="签署", callback=sign_gui)
        dpg.add_spacer(height=int(0.02 * h))
        dpg.add_text("签名：")
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag="sign_signature", readonly=True, multiline=True)
            dpg.add_button(label="复制", callback=dpg_copy_wrapper("sign_signature"))
        dpg.add_spacer(height=int(0.02 * h))

    with dpg.collapsing_header(
            label="来源验证：验证签名（使用公钥、签名）"):
        dpg.add_text("验证目标消息的签名是否有效；若有效，证明消息被私钥持有者签署，且"
                     "在签署后未被篡改。", wrap=0)
        dpg.add_spacer(height=int(0.02 * h))
        dpg.add_text("选择目标消息（文本文件）", wrap=0)
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag="verify_message", readonly=True)
            dpg.add_button(label="目标消息",
                           callback=dpg_select_file_wrapper("verify_message"))
        dpg.add_text("选择公钥", wrap=0)
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag="verify_public_key", readonly=True)
            dpg.add_button(label="公钥",
                           callback=dpg_select_file_wrapper("verify_public_key"))
        dpg.add_text("签名：")
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag="verify_signature", multiline=True)
            dpg.add_button(label="粘贴", callback=dpg_paste_wrapper("verify_signature"))
        dpg.add_button(label="验证", callback=verify_gui)
        dpg.add_spacer(height=int(0.02 * h))

    with dpg.collapsing_header(label="加密通讯：加密（使用公钥）"):
        dpg.add_text("加密消息，只有私钥持有者可以解密。", wrap=0)
        dpg.add_spacer(height=int(0.02 * h))
        dpg.add_text("选择目标消息（文本文件）", wrap=0)
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag="encrypt_message", readonly=True)
            dpg.add_button(label="目标消息", callback=encrypt_select_file)
        dpg.add_text("加密后的消息（JSON文件）保存于：", wrap=0)
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag="encrypt_save_at", readonly=True)
            dpg.add_button(label="选择文件夹",
                           callback=dpg_select_file_wrapper("encrypt_save_at"))
        dpg.add_text("选择公钥", wrap=0)
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag="encrypt_public_key", readonly=True)
            dpg.add_button(label="公钥",
                           callback=dpg_select_file_wrapper("encrypt_public_key"))
        dpg.add_checkbox(label="打开保存加密后的消息的文件夹", default_value=True,
                         tag="encrypt_open")
        dpg.add_button(label="加密", callback=encrypt_gui)
        dpg.add_spacer(height=int(0.02 * h))

    with dpg.collapsing_header(label="加密通讯：解密（使用私钥）"):
        dpg.add_text("解密消息，目标消息已被对应公钥加密。", wrap=0)
        dpg.add_spacer(height=int(0.02 * h))

        dpg.add_text("加密后的消息（JSON文件）", wrap=0)
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag="decrypt_message", readonly=True)
            dpg.add_button(label="目标消息", callback=decrypt_select_file)
        dpg.add_text("解密后的消息（文本文件）保存于：", wrap=0)
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag="decrypt_save_at", readonly=True)
            dpg.add_button(label="选择文件夹",
                           callback=dpg_select_file_wrapper("decrypt_save_at"))
        dpg.add_text("选择私钥", wrap=0)
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag="decrypt_private_key", readonly=True)
            dpg.add_button(label="私钥",
                           callback=dpg_select_file_wrapper("decrypt_private_key"))
        dpg.add_checkbox(label="打开保存解密后的消息的文件夹", default_value=True,
                         tag="decrypt_open")
        dpg.add_button(label="解密", callback=decrypt_gui)
        dpg.add_spacer(height=int(0.02 * h))

with dpg.handler_registry():
    dpg.add_mouse_wheel_handler(callback=set_font_size_mouse)
    dpg.add_mouse_click_handler(callback=set_font_size_mouse)

dpg.create_viewport(title="SHA256 with RSA", width=int(0.5 * w), height=int(0.5 * h),
                    x_pos=int(00.5 * w), y_pos=int(0.25 * h))
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("main_window", True)
dpg.start_dearpygui()
dpg.destroy_context()
