import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, init_db
from app.models.user import User
from app.models.supplier import Supplier
from app.models.product import Product

# パスワードハッシュ化関数（passlibが利用可能な場合）
try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def get_password_hash(password: str) -> str:
        """パスワードをハッシュ化"""
        return pwd_context.hash(password)
    
    ENABLE_USER_CREATION = True
except ImportError:
    print("⚠️ passlib not installed. Skipping user creation.")
    print("   To enable user creation, run: pip install passlib bcrypt")
    ENABLE_USER_CREATION = False

def seed_database():
    """テストデータの投入"""
    
    # データベース初期化
    init_db()
    
    db = SessionLocal()
    
    try:
        # テストユーザー作成（passlibがインストールされている場合のみ）
        if ENABLE_USER_CREATION:
            test_users = [
                {"email": "test1@example.com", "name": "テストユーザー1", "password": "password123"},
                {"email": "test2@example.com", "name": "テストユーザー2", "password": "password123"},
            ]
            
            for user_data in test_users:
                # 既存ユーザーチェック
                existing_user = db.query(User).filter(User.email == user_data["email"]).first()
                if not existing_user:
                    user = User(
                        email=user_data["email"],
                        name=user_data["name"],
                        hashed_password=get_password_hash(user_data["password"])
                    )
                    db.add(user)
            db.commit()
            print("✅ テストユーザーを作成しました")
        
        # 店舗データ（広島県内のお土産店）
        suppliers_data = [
            {
                "supplier_id": "s1",
                "name": "宮島工芸製作所",
                "description": "宮島細工の老舗。杓子や木工品の製造販売。",
                "address": "広島県廿日市市宮島町魚之棚町617",
                "hours": "要確認（季節変動あり）",
                "website": "https://www.miyajima-kougei.com/",
                "location": {"lat": 34.2988227, "lng": 132.3233263},
                "city": "廿日市市",
                "categories": ["木工", "宮島細工", "贈答品"]
            },
            {
                "supplier_id": "s2",
                "name": "杓子の家 宮郷",
                "description": "宮島杓子の専門店。名入れ対応あり。",
                "address": "広島県廿日市市宮島町488",
                "hours": "10:00-16:30（水休・変動あり）",
                "website": "http://www.shakushi.jp/",
                "location": {"lat": 34.298107, "lng": 132.321316},
                "city": "廿日市市",
                "categories": ["木工", "宮島杓子", "贈答品"]
            },
            {
                "supplier_id": "s3",
                "name": "宮島伝統産業会館（みやじまん工房）",
                "description": "宮島彫り・杓子作りなど体験と工芸品販売。",
                "address": "広島県廿日市市宮島町1165-9",
                "hours": "8:30-17:00（体験9:00-16:30／月休）",
                "website": "https://miyajimazaiku.com/",
                "location": {"lat": 34.30205, "lng": 132.323458},
                "city": "廿日市市",
                "categories": ["木工", "体験", "宮島彫り", "贈答品"]
            },
            {
                "supplier_id": "s4",
                "name": "対厳堂サロン（宮島御砂焼 窯元）",
                "description": "厳島神社の御砂を用いる「宮島御砂焼」の窯元直営サロン。",
                "address": "広島県廿日市市宮島口1-3-39",
                "hours": "10:30-17:30（水休・変動あり）",
                "website": "https://miyajimayaki.jp/",
                "location": {"lat": 34.310879, "lng": 132.3023},
                "city": "廿日市市",
                "categories": ["陶磁器", "宮島御砂焼", "贈答品"]
            },
            {
                "supplier_id": "s5",
                "name": "SAKURAO DISTILLERY VISITOR CENTER",
                "description": "桜尾の蒸溜所ビジターセンター。限定ウイスキー／ジン等を販売。",
                "address": "広島県廿日市市桜尾1-12-1",
                "hours": "10:00-17:00（第2日曜休）",
                "website": "https://www.sakuraodistillery.com/en/",
                "location": {"lat": 34.354424, "lng": 132.340187},
                "city": "廿日市市",
                "categories": ["酒類", "ウイスキー", "ジン", "贈答品"]
            },
            {
                "supplier_id": "s6",
                "name": "広島市現代美術館 ミュージアムショップ",
                "description": "国内外のデザイン雑貨や図録、広島ゆかりの作家グッズ。",
                "address": "広島県広島市南区比治山公園1-1",
                "hours": "10:00-17:00（月休・変動あり）",
                "website": "https://www.hiroshima-moca.jp/",
                "location": {"lat": 34.37636, "lng": 132.46982},
                "city": "広島市",
                "categories": ["ミュージアムショップ", "デザイン", "贈答品"]
            },
            {
                "supplier_id": "s7",
                "name": "広島県立美術館 ミュージアムショップ",
                "description": "県内工芸・企画展関連グッズ・図録など。",
                "address": "広島県広島市中区上幟町2-22",
                "hours": "9:00-17:00（月休・展覧会により変動）",
                "website": "https://www.hpam.jp/",
                "location": {"lat": 34.39189, "lng": 132.46952},
                "city": "広島市",
                "categories": ["ミュージアムショップ", "工芸", "贈答品"]
            },
            {
                "supplier_id": "s8",
                "name": "ひろしま美術館 ミュージアムショップ",
                "description": "美術関連グッズや広島らしいデザイン雑貨。",
                "address": "広島県広島市中区基町3-2 ひろしま美術館内",
                "hours": "9:00-17:00（企画展期間などで変動）",
                "website": "https://www.hiroshima-museum.jp/",
                "location": {"lat": 34.3972, "lng": 132.4625},
                "city": "広島市",
                "categories": ["ミュージアムショップ", "デザイン", "贈答品"]
            },
            {
                "supplier_id": "s9",
                "name": "広島城天守閣 ミュージアムショップ",
                "description": "刀剣・城関連のオリジナルグッズや和雑貨を販売。",
                "address": "広島県広島市中区基町21-1 広島城内",
                "hours": "9:00-18:00（季節により変動）",
                "website": "https://www.rijo-castle.jp/",
                "location": {"lat": 34.3992, "lng": 132.4596},
                "city": "広島市",
                "categories": ["歴史系グッズ", "和雑貨", "贈答品"]
            },
            {
                "supplier_id": "s10",
                "name": "おりづるタワー 物産館（スーベニアセレクト 人と樹）",
                "description": "広島の工芸・雑貨・銘酒をセレクトするショップ。",
                "address": "広島県広島市中区大手町1-2-1",
                "hours": "10:00-18:00（季節変動あり）",
                "website": "https://www.orizurutower.jp/",
                "location": {"lat": 34.395773, "lng": 132.454501},
                "city": "広島市",
                "categories": ["セレクトショップ", "工芸", "酒類", "贈答品"]
            },
            {
                "supplier_id": "s11",
                "name": "ひろしま夢ぷらざ（本通商店街）",
                "description": "県内各地の特産・工芸を集めたアンテナショップ。",
                "address": "広島県広島市中区本通8-28",
                "hours": "10:00-19:00",
                "website": "https://www.yumeplaza.com/",
                "location": {"lat": 34.392872, "lng": 132.459292},
                "city": "広島市",
                "categories": ["アンテナショップ", "工芸", "贈答品"]
            },
            {
                "supplier_id": "s12",
                "name": "みやじまガラス工房 Fizz Glass",
                "description": "宮島発のガラス工房。体験とオリジナル作品販売。",
                "address": "広島県廿日市市宮島町557-1",
                "hours": "10:30-17:00（不定休）",
                "website": "https://fizzglass.stores.jp/",
                "location": {"lat": 34.2997, "lng": 132.3206},
                "city": "廿日市市",
                "categories": ["ガラス", "体験", "贈答品"]
            }
        ]
        
        # IDマッピング用の辞書（文字列ID -> 数値ID）
        supplier_id_mapping = {}
        
        for supplier_data in suppliers_data:
            # 文字列IDを保存して数値IDに変換
            str_id = supplier_data.pop("supplier_id")
            
            # 既存チェック
            existing_supplier = db.query(Supplier).filter(
                Supplier.name == supplier_data["name"]
            ).first()
            
            if not existing_supplier:
                supplier = Supplier(**supplier_data)
                db.add(supplier)
                db.flush()  # IDを取得するためにflush
                supplier_id_mapping[str_id] = supplier.supplier_id
            else:
                supplier_id_mapping[str_id] = existing_supplier.supplier_id
        
        db.commit()
        
        # 商品データ
        products_data = [
            # --- s1 宮島工芸製作所 ---
            {
                "product_id": "p001",
                "name": "宮島工芸製作所 丸柄丸杓子",
                "description": "広島産ヤマザクラ材の定番しゃもじ。無塗装・研磨仕上げ。",
                "category": "木工・実用品",
                "maker": "宮島工芸製作所",
                "supplier_id": ["s1"],
                "price": 1200
            },
            {
                "product_id": "p002",
                "name": "宮島工芸製作所 ナナメターナーS",
                "description": "フライパン調理に使いやすい斜めターナー。",
                "category": "木工・キッチン",
                "maker": "宮島工芸製作所",
                "supplier_id": ["s1"],
                "price": 980
            },
            {
                "product_id": "p003",
                "name": "宮島工芸製作所 飾り杓子（中）",
                "description": "来客・贈答向けの飾り杓子。",
                "category": "木工・縁起物",
                "maker": "宮島工芸製作所",
                "supplier_id": ["s1"],
                "price": 2500
            },
            {
                "product_id": "p004",
                "name": "宮島工芸製作所 バターナイフ（桜）",
                "description": "手当たりの良い桜材の小型カトラリー。",
                "category": "木工・カトラリー",
                "maker": "宮島工芸製作所",
                "supplier_id": ["s1"],
                "price": 650
            },
            {
                "product_id": "p005",
                "name": "宮島工芸製作所 しゃもじ台",
                "description": "しゃもじ用スタンド。宮島の木工仕立て。",
                "category": "木工・キッチン",
                "maker": "宮島工芸製作所",
                "supplier_id": ["s1"],
                "price": 800
            },
            # --- s2 杓子の家 ---
            {
                "product_id": "p006",
                "name": "看板杓子（セミオーダー名入れ）",
                "description": "店頭/オンラインで名入れ対応の大型飾り杓子。",
                "category": "木工・縁起物",
                "maker": "杓子の家",
                "supplier_id": ["s2"],
                "price": 5800
            },
            {
                "product_id": "p007",
                "name": "実用しゃもじ（名入れ対応）",
                "description": "家庭用サイズの実用しゃもじ。名入れ可。",
                "category": "木工・実用品",
                "maker": "杓子の家",
                "supplier_id": ["s2"],
                "price": 1500
            },
            {
                "product_id": "p008",
                "name": "杓子ストラップ（名入れサービス）",
                "description": "木製ストラップ（※雑貨カテゴリではなく木工小物として実用品扱い）。",
                "category": "木工・小物",
                "maker": "杓子の家",
                "supplier_id": ["s2"],
                "price": 480
            },
            {
                "product_id": "p009",
                "name": "飾り杓子（祈祷代行対応）",
                "description": "厳島神社への祈祷代行に対応する大型飾り杓子。",
                "category": "木工・縁起物",
                "maker": "杓子の家",
                "supplier_id": ["s2"],
                "price": 8500
            },
            {
                "product_id": "p010",
                "name": "杓子壁掛け台",
                "description": "飾り杓子用の壁掛け台。",
                "category": "木工・小物",
                "maker": "杓子の家",
                "supplier_id": ["s2"],
                "price": 1200
            },
            # --- s3 宮島伝統産業会館 ---
            {
                "product_id": "p011",
                "name": "宮島彫り 丸盆 15cm",
                "description": "体験でも使用される定番サイズ。伝統工芸士監修。",
                "category": "木工・宮島彫り",
                "maker": "宮島細工協同組合",
                "supplier_id": ["s3"],
                "price": 3800
            },
            {
                "product_id": "p012",
                "name": "宮島彫り 小皿（紅葉文様）",
                "description": "彫り文様が映える銘々皿。",
                "category": "木工・宮島彫り",
                "maker": "宮島細工協同組合",
                "supplier_id": ["s3"],
                "price": 2200
            },
            {
                "product_id": "p013",
                "name": "宮島彫り 茶托 5客",
                "description": "来客向けの茶托セット。",
                "category": "木工・宮島彫り",
                "maker": "宮島細工協同組合",
                "supplier_id": ["s3"],
                "price": 6500
            },
            {
                "product_id": "p014",
                "name": "宮島杓子（宮島伝統産業会館セレクト）",
                "description": "伝統工芸の基準を満たす杓子。",
                "category": "木工・実用品",
                "maker": "宮島細工協同組合",
                "supplier_id": ["s3"],
                "price": 1800
            },
            {
                "product_id": "p015",
                "name": "木工カトラリー（へら／ターナー）",
                "description": "宮島の木工実用品。",
                "category": "木工・キッチン",
                "maker": "宮島細工協同組合",
                "supplier_id": ["s3"],
                "price": 1200
            },
            # --- s4 対厳堂 ---
            {
                "product_id": "p016",
                "name": "御砂焼 酒器セット（徳利・盃）",
                "description": "厳島神社ゆかりの御砂焼による酒器。",
                "category": "陶芸・酒器",
                "maker": "対厳堂",
                "supplier_id": ["s4"],
                "price": 12000
            },
            {
                "product_id": "p017",
                "name": "御砂焼 花器（中）",
                "description": "御砂を用いる伝統の花器。",
                "category": "陶芸・花器",
                "maker": "対厳堂",
                "supplier_id": ["s4"],
                "price": 8500
            },
            {
                "product_id": "p018",
                "name": "御砂焼 抹茶碗",
                "description": "茶の湯向けの茶碗。",
                "category": "陶芸・茶道具",
                "maker": "対厳堂",
                "supplier_id": ["s4"],
                "price": 15000
            },
            {
                "product_id": "p019",
                "name": "御砂焼 ぐい呑",
                "description": "掌に収まる盃。贈答に人気。",
                "category": "陶芸・酒器",
                "maker": "対厳堂",
                "supplier_id": ["s4"],
                "price": 3500
            },
            {
                "product_id": "p020",
                "name": "御砂焼 香立て",
                "description": "インテリア小物としての香立て。",
                "category": "陶芸・インテリア",
                "maker": "対厳堂",
                "supplier_id": ["s4"],
                "price": 2800
            },
            # --- s5 SAKURAO DISTILLERY ---
            {
                "product_id": "p021",
                "name": "SAKURAO Single Malt（桜尾シングルモルト）",
                "description": "桜尾蒸留所のシングルモルト。",
                "category": "酒類・ウイスキー",
                "maker": "SAKURAO DISTILLERY",
                "supplier_id": ["s5"],
                "price": 8800
            },
            {
                "product_id": "p022",
                "name": "TOGOUCHI Whisky（戸河内）",
                "description": "ブレンデッド/モルトのラインアップ。",
                "category": "酒類・ウイスキー",
                "maker": "SAKURAO DISTILLERY",
                "supplier_id": ["s5"],
                "price": 4500
            },
            {
                "product_id": "p023",
                "name": "SAKURAO GIN Original",
                "description": "瀬戸内ボタニカルのクラフトジン。",
                "category": "酒類・ジン",
                "maker": "SAKURAO DISTILLERY",
                "supplier_id": ["s5"],
                "price": 3800
            },
            {
                "product_id": "p024",
                "name": "SAKURAO GIN Limited（季節限定）",
                "description": "限定ボタニカルを配した蒸留所限定ボトル。",
                "category": "酒類・ジン",
                "maker": "SAKURAO DISTILLERY",
                "supplier_id": ["s5"],
                "price": 5500
            },
            {
                "product_id": "p025",
                "name": "SAKURAO シングルモルト ピーテッド",
                "description": "ピート由来の個性派。",
                "category": "酒類・ウイスキー",
                "maker": "SAKURAO DISTILLERY",
                "supplier_id": ["s5"],
                "price": 9800
            },
            {
                "product_id": "p026",
                "name": "桜尾 樽熟成ジン",
                "description": "樽由来の風味をまとったジン。",
                "category": "酒類・ジン",
                "maker": "SAKURAO DISTILLERY",
                "supplier_id": ["s5"],
                "price": 6200
            },
            {
                "product_id": "p027",
                "name": "桜尾 オリジナルグラス",
                "description": "蒸留所オリジナルのドリンキンググラス。",
                "category": "酒器・グラス",
                "maker": "SAKURAO DISTILLERY",
                "supplier_id": ["s5"],
                "price": 1800
            },
            {
                "product_id": "p028",
                "name": "桜尾 テイスティンググラス",
                "description": "ウイスキー・ジン向けの小型グラス。",
                "category": "酒器・グラス",
                "maker": "SAKURAO DISTILLERY",
                "supplier_id": ["s5"],
                "price": 1200
            },
            # --- s6 広島市現代美術館 ---
            {
                "product_id": "p029",
                "name": "広島市現代美術館 展覧会カタログ（339取扱）",
                "description": "MOCA開催展の公式図録。",
                "category": "アートブック",
                "maker": "広島市現代美術館",
                "supplier_id": ["s6"],
                "price": 2500
            },
            {
                "product_id": "p030",
                "name": "339 オリジナルグッズ（ポスター等）",
                "description": "展覧会関連のビジュアルグッズ。",
                "category": "ミュージアムグッズ",
                "maker": "広島市現代美術館",
                "supplier_id": ["s6"],
                "price": 1500
            },
            {
                "product_id": "p031",
                "name": "339 トートバッグ（ロゴ/作品モチーフ）",
                "description": "館ショップ発のキャンバストート。",
                "category": "バッグ",
                "maker": "広島市現代美術館",
                "supplier_id": ["s6"],
                "price": 2800
            },
            {
                "product_id": "p032",
                "name": "339 ポストカードセット",
                "description": "展示作品モチーフのカード。",
                "category": "紙文具",
                "maker": "広島市現代美術館",
                "supplier_id": ["s6"],
                "price": 600
            },
            # --- s7 広島県立美術館 ---
            {
                "product_id": "p033",
                "name": "広島県立美術館 図録（所蔵品/特別展）",
                "description": "県美発行の展覧会図録。",
                "category": "アートブック",
                "maker": "広島県立美術館",
                "supplier_id": ["s7"],
                "price": 2800
            },
            {
                "product_id": "p034",
                "name": "広島県立美術館 絵はがきセット",
                "description": "所蔵品モチーフのポストカード。",
                "category": "紙文具",
                "maker": "広島県立美術館",
                "supplier_id": ["s7"],
                "price": 500
            },
            {
                "product_id": "p035",
                "name": "広島県立美術館 クリアファイル",
                "description": "展覧会ビジュアルのクリアファイル。",
                "category": "文具",
                "maker": "広島県立美術館",
                "supplier_id": ["s7"],
                "price": 350
            },
            # --- s8 ひろしま美術館 ---
            {
                "product_id": "p036",
                "name": "ひろしま美術館 黒猫マグカップ",
                "description": "館オリジナルの人気マグ。",
                "category": "テーブルウェア",
                "maker": "ひろしま美術館",
                "supplier_id": ["s8"],
                "price": 1800
            },
            {
                "product_id": "p037",
                "name": "箸置き「ドービニーの庭」6個セット",
                "description": "名画が完成するアクリル製箸置き。",
                "category": "テーブルウェア",
                "maker": "ひろしま美術館",
                "supplier_id": ["s8"],
                "price": 2400
            },
            {
                "product_id": "p038",
                "name": "所蔵作品 刺繍ソックス",
                "description": "所蔵作品をモチーフにした刺繍入り靴下。",
                "category": "テキスタイル小物",
                "maker": "ひろしま美術館",
                "supplier_id": ["s8"],
                "price": 980
            },
            {
                "product_id": "p039",
                "name": "ひろしま美術館 図録（所蔵/企画展）",
                "description": "館発行の公式カタログ。",
                "category": "アートブック",
                "maker": "ひろしま美術館",
                "supplier_id": ["s8"],
                "price": 3000
            },
            {
                "product_id": "p040",
                "name": "ひろしま美術館 オリジナルトート",
                "description": "作品モチーフのキャンバストート。",
                "category": "バッグ",
                "maker": "ひろしま美術館",
                "supplier_id": ["s8"],
                "price": 2500
            },
            {
                "product_id": "p041",
                "name": "ひろしま美術館 ポストカード",
                "description": "コレクションモチーフのポストカード。",
                "category": "紙文具",
                "maker": "ひろしま美術館",
                "supplier_id": ["s8"],
                "price": 150
            },
            # --- s9 広島城 ---
            {
                "product_id": "p042",
                "name": "広島城 御城印",
                "description": "天守閣ショップで頒布される御城印。",
                "category": "和紙・記念印",
                "maker": "広島城",
                "supplier_id": ["s9"],
                "price": 500
            },
            {
                "product_id": "p043",
                "name": "広島城 図録（企画展）",
                "description": "歴史・考古関連の展覧会図録。",
                "category": "アートブック/歴史",
                "maker": "広島城",
                "supplier_id": ["s9"],
                "price": 2000
            },
            {
                "product_id": "p044",
                "name": "広島城 書籍（城史関連）",
                "description": "広島城の歴史に関する書籍。",
                "category": "書籍",
                "maker": "広島城",
                "supplier_id": ["s9"],
                "price": 1800
            },
            {
                "product_id": "p045",
                "name": "広島城 オリジナル手拭い",
                "description": "城モチーフの和柄手拭い。",
                "category": "テキスタイル",
                "maker": "広島城",
                "supplier_id": ["s9"],
                "price": 1200
            },
            # --- s11 ひろしま夢ぷらざ ---
            {
                "product_id": "p046",
                "name": "熊野筆 化粧ブラシ（竹田ブラシ製作所）",
                "description": "県内老舗ブランドのメイクブラシ。",
                "category": "ビューティーツール",
                "maker": "竹田ブラシ製作所",
                "supplier_id": ["s11"],
                "price": 5800
            },
            {
                "product_id": "p047",
                "name": "熊野筆 携帯リップブラシ",
                "description": "外出先で使いやすい携帯タイプ。",
                "category": "ビューティーツール",
                "maker": "竹田ブラシ製作所",
                "supplier_id": ["s11"],
                "price": 2200
            },
            # --- s12 みやじまガラス工房 ---
            {
                "product_id": "p048",
                "name": "FizzGlass 一輪挿し",
                "description": "宮島の工房で手づくりされた小花向け花器。",
                "category": "ガラス工芸",
                "maker": "Miyajima Glass Studio FizzGlass",
                "supplier_id": ["s12"],
                "price": 3800
            },
            {
                "product_id": "p049",
                "name": "FizzGlass ガラスアクセサリー（ペンダント）",
                "description": "ボトル再生ガラス等を用いたアクセサリー。",
                "category": "ガラス工芸・アクセサリー",
                "maker": "Miyajima Glass Studio FizzGlass",
                "supplier_id": ["s12"],
                "price": 2800
            },
            {
                "product_id": "p050",
                "name": "FizzGlass サンキャッチャー",
                "description": "光を受けて室内に彩りを届ける吊り飾り。",
                "category": "ガラス工芸・インテリア",
                "maker": "Miyajima Glass Studio FizzGlass",
                "supplier_id": ["s12"],
                "price": 4200
            }
        ]
        
        # 商品データの投入
        for product_data in products_data:
            # product_idは文字列なので削除（DBの自動採番を使用）
            product_data.pop("product_id")
            
            # supplier_idを取得して削除
            supplier_id = product_data.pop("supplier_id")
            
            # 各店舗IDに対して商品を作成
            for store_id in supplier_id:
                if store_id in supplier_id_mapping:
                    # 既存商品チェック
                    existing_product = db.query(Product).filter(
                        Product.name == product_data["name"],
                        Product.supplier_id == supplier_id_mapping[store_id]
                    ).first()
                    
                    if not existing_product:
                        product = Product(
                            supplier_id=supplier_id_mapping[store_id],
                            **product_data
                        )
                        db.add(product)
        
        db.commit()
        print("✅ テストデータの投入が完了しました！")
        
        # 投入されたデータの統計
        if ENABLE_USER_CREATION:
            user_count = db.query(User).count()
            print(f"  - ユーザー: {user_count}件")
        supplier_count = db.query(Supplier).count()
        product_count = db.query(Product).count()
        
        print(f"📊 データ統計:")
        print(f"  - 店舗: {supplier_count}件")
        print(f"  - 商品: {product_count}件")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()