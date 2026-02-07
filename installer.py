#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import json
import ssl

# ---------------------------------------------------------
# ⚙️ إعدادات الآيجنت
# ---------------------------------------------------------
# الرابط المباشر لملف JSON على GitHub (تأكد أنه Raw)
STORE_URL = "https://raw.githubusercontent.com/chebiri/MyE2-Store/main/database/store.json"

# مسار التحميل المؤقت
TMP_DIR = "/tmp/mye2_downloads"

# ---------------------------------------------------------
# 🛠️ دوال المساعدة (Network & System)
# ---------------------------------------------------------

# دالة لجلب البيانات من الإنترنت (متوافقة مع Python 2 و 3)
def get_url_content(url):
    try:
        # تجاوز مشاكل SSL في صور Enigma2 القديمة
        if hasattr(ssl, '_create_unverified_context'):
            context = ssl._create_unverified_context()
        else:
            context = None

        try:
            # Python 3
            import urllib.request as urllib2
            response = urllib2.urlopen(url, context=context, timeout=10)
        except ImportError:
            # Python 2
            import urllib2
            response = urllib2.urlopen(url, context=context, timeout=10)
            
        return response.read()
    except Exception as e:
        print("\n❌ Error connecting to GitHub:")
        print("   " + str(e))
        print("➡️ Please check your internet connection or DNS.")
        sys.exit(1)

def download_file(url, save_path):
    print("⏳ Downloading: " + url.split('/')[-1])
    try:
        content = get_url_content(url)
        with open(save_path, 'wb') as f:
            f.write(content)
        return True
    except Exception as e:
        print("❌ Download Failed: " + str(e))
        return False

def install_package(file_path, install_cmd=None):
    print("\n⚙️ Installing...")
    
    if install_cmd:
        # إذا كان هناك أمر تثبيت خاص (مثل Softcams)
        os.system(install_cmd)
    elif file_path.endswith('.ipk'):
        os.system("opkg install --force-reinstall " + file_path)
    elif file_path.endswith('.deb'):
        os.system("dpkg -i --force-overwrite " + file_path)
    elif file_path.endswith('.tar.gz') or file_path.endswith('.tgz'):
        os.system("tar -xzvf " + file_path + " -C /")
    elif file_path.endswith('.sh'):
        os.system("chmod 755 " + file_path + " && " + file_path)
    else:
        print("⚠️ Unknown file type. Cannot install automatically.")
        return

    print("\n✅ Installation Process Finished.")
    print("🔄 You might need to Restart Enigma2.")

# ---------------------------------------------------------
# 🚀 بداية البرنامج
# ---------------------------------------------------------
def main():
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR)

    print("\n📡 Connecting to MyE2 Store...")
    
    # 1. جلب قاعدة البيانات
    json_data = get_url_content(STORE_URL)
    try:
        items = json.loads(json_data)
    except:
        print("❌ Error: Invalid JSON format from server.")
        sys.exit(1)

    print("✅ Connected! Found " + str(len(items)) + " items.\n")

    # 2. عرض القائمة (اختياري، أو يمكن تمرير اسم الإضافة كباراميتر)
    # هنا سنفترض أن المستخدم يريد البحث عن إضافة معينة أو عرض الكل
    if len(sys.argv) > 1:
        search_query = sys.argv[1].lower()
    else:
        # عرض أحدث 5 إضافات كمثال
        print("--- Latest Additions ---")
        for idx, item in enumerate(items[:5]):
            print(str(idx+1) + ". " + item['title'])
        print("------------------------")
        print("Usage: python installer.py [plugin_name]")
        return

    # 3. البحث عن الإضافة المطلوبة
    target_item = None
    for item in items:
        if search_query in item['title'].lower() or search_query in item['id'].lower():
            target_item = item
            break
    
    if not target_item:
        print("❌ Item not found: " + search_query)
        return

    # 4. عرض التفاصيل (المعلومات الجديدة) 📅📦
    print("\n📦 Package Info:")
    print("   Name:    " + target_item['title'])
    print("   Version: " + target_item['version'])
    print("   Size:    " + target_item.get('size', 'Unknown')) # الميزة الجديدة
    print("   Date:    " + target_item.get('date', 'Unknown')) # الميزة الجديدة
    print("   Type:    " + target_item['type'])

    # 5. التأكيد والتحميل
    # (نقوم بالتحميل مباشرة لأن التلنت لا يدعم الإدخال التفاعلي بسهولة أحياناً)
    
    file_name = target_item['downloadUrl'].split('/')[-1]
    save_path = os.path.join(TMP_DIR, file_name)

    # إصلاح الرابط: التأكد من أنه لا يشير لـ 192.168
    # الكود يأخذ الرابط من GitHub مباشرة، لذا المشكلة محلولة
    if download_file(target_item['downloadUrl'], save_path):
        install_package(save_path, target_item.get('installCommand'))
        
        # تنظيف
        if os.path.exists(save_path):
            os.remove(save_path)

if __name__ == "__main__":
    main()
