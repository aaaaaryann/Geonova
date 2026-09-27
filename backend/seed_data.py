import datetime
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
import models
from security import hash_password

STATE_BANNERS = {
    "JK": "https://images.unsplash.com/photo-1527838832700-5059252407fa?auto=format&fit=crop&w=1200&q=80",
    "HP": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=1200&q=80",
    "PB": "https://images.unsplash.com/photo-1588096344356-9b4974f37475?auto=format&fit=crop&w=1200&q=80",
    "HR": "https://images.unsplash.com/photo-1605152276897-4f618f831968?auto=format&fit=crop&w=1200&q=80",
    "UK": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=1200&q=80",
    "UP": "https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=1200&q=80",
    "RJ": "https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=1200&q=80",
    "DL": "https://images.unsplash.com/photo-1587474260584-136574528ed5?auto=format&fit=crop&w=1200&q=80",
    "CH": "https://images.unsplash.com/photo-1605152276897-4f618f831968?auto=format&fit=crop&w=1200&q=80",
    "LA": "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=1200&q=80",
    "GJ": "https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=1200&q=80",
    "MH": "https://images.unsplash.com/photo-1529253355930-ddbe423a2ac7?auto=format&fit=crop&w=1200&q=80",
    "GA": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=1200&q=80",
    "MP": "https://images.unsplash.com/photo-1597074866923-dc0589150358?auto=format&fit=crop&w=1200&q=80",
    "CG": "https://images.unsplash.com/photo-1518457607834-6e8d80c183c5?auto=format&fit=crop&w=1200&q=80",
    "DNHDD": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
    "BR": "https://images.unsplash.com/photo-1604644401890-0bd678c83788?auto=format&fit=crop&w=1200&q=80",
    "JH": "https://images.unsplash.com/photo-1505118380757-91f5f5632de0?auto=format&fit=crop&w=1200&q=80",
    "OD": "https://images.unsplash.com/photo-1558431382-27e303142255?auto=format&fit=crop&w=1200&q=80",
    "WB": "https://images.unsplash.com/photo-1558431382-27e303142255?auto=format&fit=crop&w=1200&q=80",
    "SK": "https://images.unsplash.com/photo-1589182373726-e4f658ab50f0?auto=format&fit=crop&w=1200&q=80",
    "AN": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
    "AP": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=1200&q=80",
    "TG": "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=1200&q=80",
    "KA": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=1200&q=80",
    "KL": "https://images.unsplash.com/photo-1593104547489-5cfb3839a3b5?auto=format&fit=crop&w=1200&q=80",
    "TN": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1200&q=80",
    "PY": "https://images.unsplash.com/photo-1584450150050-4b9bdbd51f68?auto=format&fit=crop&w=1200&q=80",
    "LD": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
    "AS": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=1200&q=80",
    "AR": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=1200&q=80",
    "MN": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=1200&q=80",
    "ML": "https://images.unsplash.com/photo-1470252649378-9c29740c9fa8?auto=format&fit=crop&w=1200&q=80",
    "MZ": "https://images.unsplash.com/photo-1499678329028-101435549a4e?auto=format&fit=crop&w=1200&q=80",
    "NL": "https://images.unsplash.com/photo-1499678329028-101435549a4e?auto=format&fit=crop&w=1200&q=80",
    "TR": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1200&q=80",
}

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded and refresh state banners if needed.
        existing_state_count = db.query(models.StateUT).count()
        if existing_state_count >= 36:
            print("Database already contains all 36 States & UTs. Refreshing state banners to the matching images.")
            for state in db.query(models.StateUT).all():
                exact = STATE_BANNERS.get(state.code)
                if exact and state.banner_image != exact:
                    state.banner_image = exact
            db.commit()
            return

        print("Seeding Geonova database with all 28 States, 8 UTs, safety protocols, geofences, and default accounts...")

        # 1. Seed Users
        admin_user = models.User(
            full_name="Rajesh Sharma (Chief Safety Admin)",
            email="admin@geonova.in",
            phone_number="+91 9876543210",
            password_hash=hash_password("Admin@123"),
            role="admin",
            nationality="Indian",
            preferred_language="English"
        )
        db.add(admin_user)

        tourist_user = models.User(
            full_name="Aarav Mehta",
            email="tourist@geonova.in",
            phone_number="+91 9811122233",
            password_hash=hash_password("Tourist@123"),
            role="tourist",
            nationality="Indian",
            preferred_language="English",
            medical_notes="Allergic to penicillin. Type O+ blood."
        )
        db.add(tourist_user)

        provider_user = models.User(
            full_name="Himalayan Wonders & Heritage Tours",
            email="provider@geonova.in",
            phone_number="+91 9822233344",
            password_hash=hash_password("Provider@123"),
            role="provider",
            nationality="Indian",
            preferred_language="English"
        )
        db.add(provider_user)

        authority_user = models.User(
            full_name="Delhi & Tourist Police Assistance Cell",
            email="police@geonova.in",
            phone_number="112",
            password_hash=hash_password("Police@123"),
            role="authority",
            nationality="Indian",
            preferred_language="Hindi & English"
        )
        db.add(authority_user)
        db.flush()

        # Tourist emergency contacts
        contact1 = models.EmergencyContact(
            user_id=tourist_user.id,
            name="Sunita Mehta",
            relationship_type="Mother",
            phone_number="+91 9811199988",
            email="sunita.m@gmail.com",
            is_primary=True
        )
        contact2 = models.EmergencyContact(
            user_id=tourist_user.id,
            name="Vikram Mehta",
            relationship_type="Brother",
            phone_number="+91 9811177766",
            email="vikram.m@gmail.com",
            is_primary=False
        )
        db.add_all([contact1, contact2])

        # Tourist Subscription
        tourist_sub = models.Subscription(
            user_id=tourist_user.id,
            plan="premium",
            amount=499.0,
            is_active=True,
            expires_at=datetime.datetime.utcnow() + datetime.timedelta(days=365)
        )
        db.add(tourist_sub)

        # 2. All 28 States and 8 Union Territories (Exact 36 Entities)
        states_data = [
            # --- Northern India (10: 7 states, 3 UTs) ---
            {
                "code": "JK",
                "name": "Jammu and Kashmir",
                "category": "union_territory",
                "region": "Northern",
                "capital": "Srinagar (Summer), Jammu (Winter)",
                "banner_image": "https://images.unsplash.com/photo-1595815771614-ade9d652a65d?auto=format&fit=crop&w=1200&q=80",
                "description": "Known as 'Paradise on Earth', famed for snow-capped Pir Panjal peaks, Dal Lake houseboats, Mughal gardens, and spiritual shrines.",
                "best_season": "April to October (Pleasant), December to March (Snow sports)",
                "official_website": "https://jktourism.jk.gov.in",
                "culture_traditions": "Kashmiri Sufiyana music, intricate Pashmina weaving, papier-mâché craft, and warmth of Kahwa hospitality.",
                "local_food": "Rogan Josh, Gushtaba, Modur Pulao, Yakhni, and Kashmiri Kahwa tea.",
                "emergency_helpline": "112 / Tourist Police: +91-194-2450700",
                "destinations": [
                    {"name": "Dal Lake & Houseboats", "category": "Natural", "desc": "Iconic lake with floating shikaras and historic houseboats.", "lat": 34.0837, "lng": 74.8370, "img": "https://images.unsplash.com/photo-1595815771614-ade9d652a65d?auto=format&fit=crop&w=600&q=80", "fee": "INR 500-1500 (Shikara)"},
                    {"name": "Gulmarg Gondola", "category": "Adventure", "desc": "One of the highest cable cars in the world offering world-class skiing.", "lat": 34.0484, "lng": 74.3805, "img": "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=600&q=80", "fee": "INR 740 - 1690"}
                ]
            },
            {
                "code": "HP",
                "name": "Himachal Pradesh",
                "category": "state",
                "region": "Northern",
                "capital": "Shimla (Summer), Dharamshala (Winter)",
                "banner_image": "https://images.unsplash.com/photo-1605649487212-47bdab064df8?auto=format&fit=crop&w=1200&q=80",
                "description": "The Land of the Gods (Devbhoomi), offering Himalayan pine forests, adventure trails, Buddhist monasteries, and river valleys.",
                "best_season": "March to June (Summer), October to February (Winter & Snowfall)",
                "official_website": "https://himachaltourism.gov.in",
                "culture_traditions": "Himachali Nati folk dance, Kullu shawl handicrafts, and peaceful Tibetan Buddhist monasteries.",
                "local_food": "Dham (festive feast), Siddu, Madra, Chha Gosht, and Babru.",
                "emergency_helpline": "112 / +91-177-2625864",
                "destinations": [
                    {"name": "Rohtang Pass & Solang Valley", "category": "Adventure", "desc": "High mountain pass at 3,978m connecting Kullu and Lahaul.", "lat": 32.3716, "lng": 77.2466, "img": "https://images.unsplash.com/photo-1586861635167-e5223aadc9fe?auto=format&fit=crop&w=600&q=80", "fee": "Permit required"},
                    {"name": "Dharamshala & McLeodganj", "category": "Cultural", "desc": "Residence of His Holiness the Dalai Lama and center of Tibetan culture.", "lat": 32.2190, "lng": 76.3234, "img": "https://images.unsplash.com/photo-1579618218290-24a26f63a708?auto=format&fit=crop&w=600&q=80", "fee": "Free"}
                ]
            },
            {
                "code": "PB",
                "name": "Punjab",
                "category": "state",
                "region": "Northern",
                "capital": "Chandigarh",
                "banner_image": "https://images.unsplash.com/photo-1588096344356-9b4974f37475?auto=format&fit=crop&w=1200&q=80",
                "description": "The heartland of vibrant culture, rich Sikh history, lush mustard fields, and extraordinary hospitality.",
                "best_season": "October to March",
                "official_website": "https://punjabtourism.punjab.gov.in",
                "culture_traditions": "Bhangra and Giddha dance, Phulkari embroidery, and sacred Langar community service.",
                "local_food": "Makki di Roti & Sarson da Saag, Butter Chicken, Amritsari Kulcha, and rich Sweet Lassi.",
                "emergency_helpline": "112 / +91-183-2553954",
                "destinations": [
                    {"name": "Golden Temple (Harmandir Sahib)", "category": "Pilgrimage", "desc": "The spiritual centerpiece of Sikhism renowned for peace, gold facade, and 24/7 Langar.", "lat": 31.6200, "lng": 74.8765, "img": "https://images.unsplash.com/photo-1588096344356-9b4974f37475?auto=format&fit=crop&w=600&q=80", "fee": "Free"},
                    {"name": "Wagah Border Ceremony", "category": "Historical", "desc": "High-energy military retreat ceremony between India and Pakistan.", "lat": 31.6044, "lng": 74.5732, "img": "https://images.unsplash.com/photo-1584646098378-0874589d76b1?auto=format&fit=crop&w=600&q=80", "fee": "Free"}
                ]
            },
            {
                "code": "HR",
                "name": "Haryana",
                "category": "state",
                "region": "Northern",
                "capital": "Chandigarh",
                "banner_image": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80",
                "description": "The cradle of Vedic civilization, home to sacred Kurukshetra, scenic Morni Hills, and dynamic modern hub Gurugram.",
                "best_season": "October to March",
                "official_website": "https://haryanatourism.gov.in",
                "culture_traditions": "Saang folk theater, Ragini music, traditional pottery, and Surajkund International Crafts Mela.",
                "local_food": "Bajra Khichdi, Kachri ki Sabzi, Churma, and fresh churned lassi.",
                "emergency_helpline": "112 / 1091 (Women)",
                "destinations": [
                    {"name": "Brahma Sarovar, Kurukshetra", "category": "Pilgrimage", "desc": "Ancient holy water tank associated with Mahabharata history.", "lat": 29.9678, "lng": 76.8378, "img": "https://images.unsplash.com/photo-1609137144822-263a76383637?auto=format&fit=crop&w=600&q=80", "fee": "Free"},
                    {"name": "Sultanpur Bird Sanctuary", "category": "Natural", "desc": "Popular national park sheltering over 250 species of resident and migratory birds.", "lat": 28.4616, "lng": 76.8923, "img": "https://images.unsplash.com/photo-1552728089-57bdde30beb3?auto=format&fit=crop&w=600&q=80", "fee": "INR 50"}
                ]
            },
            {
                "code": "UK",
                "name": "Uttarakhand",
                "category": "state",
                "region": "Northern",
                "capital": "Dehradun (Winter), Gairsain (Summer)",
                "banner_image": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=1200&q=80",
                "description": "Devbhoomi with the sacred Ganga and Yamuna origins, Himalayan peaks, yoga sanctuaries of Rishikesh, and the Chota Char Dham.",
                "best_season": "March to June, September to November",
                "official_website": "https://uttarakhandtourism.gov.in",
                "culture_traditions": "Garhwali and Kumaoni folk dances, Chholiya sword dance, and Ganga Aarti ceremonies.",
                "local_food": "Kafuli, Chainssoo, Aloo ke Gutke, Jhangore ki Kheer, and Bal Mithai.",
                "emergency_helpline": "112 / SDRF: 1070",
                "destinations": [
                    {"name": "Rishikesh Yoga & Rafting Capital", "category": "Adventure", "desc": "World yoga sanctuary with Ganges river rafting and evening Triveni Ghat Aarti.", "lat": 30.0869, "lng": 78.2676, "img": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=600&q=80", "fee": "Varies by activity"},
                    {"name": "Jim Corbett National Park", "category": "Natural", "desc": "India's oldest national park known for Bengal tigers and jungle safaris.", "lat": 29.5300, "lng": 78.7747, "img": "https://images.unsplash.com/photo-1561731216-c3a4d99437d5?auto=format&fit=crop&w=600&q=80", "fee": "INR 1000 - 4500 (Safari)"}
                ]
            },
            {
                "code": "UP",
                "name": "Uttar Pradesh",
                "category": "state",
                "region": "Northern",
                "capital": "Lucknow",
                "banner_image": "https://images.unsplash.com/photo-1564507592333-c60657eea523?auto=format&fit=crop&w=1200&q=80",
                "description": "India's historical heartland featuring the Taj Mahal, eternal Varanasi ghats, royal Awadhi monuments, and Prayagraj Sangam.",
                "best_season": "October to March",
                "official_website": "https://uptourism.gov.in",
                "culture_traditions": "Kathak classical dance, Chikankari embroidery, Benarasi silk weaving, and brass crafts of Moradabad.",
                "local_food": "Lucknowi Galouti Kebabs, Banarasi Paan, Bedmi Puri, and Petha of Agra.",
                "emergency_helpline": "112 / UP Tourist Helpline: 1800-180-5013",
                "destinations": [
                    {"name": "Taj Mahal, Agra", "category": "Historical", "desc": "UNESCO World Heritage Wonder of the World and white marble mausoleum of love.", "lat": 27.1751, "lng": 78.0421, "img": "https://images.unsplash.com/photo-1564507592333-c60657eea523?auto=format&fit=crop&w=600&q=80", "fee": "INR 50 (Indians) / 1100 (Foreigners)"},
                    {"name": "Varanasi Ghats & Kashi Vishwanath", "category": "Pilgrimage", "desc": "The spiritual capital of India on the sacred Ganges river with magical evening Aarti.", "lat": 25.3176, "lng": 82.9739, "img": "https://images.unsplash.com/photo-1561361513-2d000a50f0dc?auto=format&fit=crop&w=600&q=80", "fee": "Free"}
                ]
            },
            {
                "code": "RJ",
                "name": "Rajasthan",
                "category": "state",
                "region": "Northern",
                "capital": "Jaipur",
                "banner_image": "https://images.unsplash.com/photo-1599661046289-e31897846e41?auto=format&fit=crop&w=1200&q=80",
                "description": "The Land of Kings, world-famous for majestic hill forts, Thar Desert dunes, royal Rajput palaces, and vibrant heritage festivals.",
                "best_season": "October to March",
                "official_website": "https://tourism.rajasthan.gov.in",
                "culture_traditions": "Ghoomar and Kalbelia dance, puppetry (Kathputli), block printing, and Bandhani tie-dye textiles.",
                "local_food": "Dal Baati Churma, Laal Maas, Ker Sangri, Gatte ki Sabzi, and Ghevar.",
                "emergency_helpline": "112 / Tourist Police: +91-141-2822830",
                "destinations": [
                    {"name": "Amber Fort & Palace, Jaipur", "category": "Historical", "desc": "Magnificent hilltop fort blending Hindu and Mughal architecture overlooking Maota Lake.", "lat": 26.9855, "lng": 75.8513, "img": "https://images.unsplash.com/photo-1599661046289-e31897846e41?auto=format&fit=crop&w=600&q=80", "fee": "INR 100 / 500"},
                    {"name": "Sam Sand Dunes, Jaisalmer", "category": "Adventure", "desc": "Golden Thar Desert camel safaris, starlit camping, and desert musical evenings.", "lat": 26.8322, "lng": 70.5050, "img": "https://images.unsplash.com/photo-1509299349698-dd22323b5963?auto=format&fit=crop&w=600&q=80", "fee": "Varies by safari"}
                ]
            },
            {
                "code": "DL",
                "name": "Delhi",
                "category": "union_territory",
                "region": "Northern",
                "capital": "New Delhi",
                "banner_image": "https://images.unsplash.com/photo-1587474260584-136574528ed5?auto=format&fit=crop&w=1200&q=80",
                "description": "India's historic and political capital, weaving centuries of Mughal architecture, British colonial avenues, and modern cosmopolitan life.",
                "best_season": "October to March",
                "official_website": "https://delhitourism.gov.in",
                "culture_traditions": "Qawwali nights at Nizamuddin Dargah, Dilli Haat artisan crafts, and rich theater scene.",
                "local_food": "Chandni Chowk Parathas, Chole Bhature, Butter Chicken, and Dahi Bhalla.",
                "emergency_helpline": "112 / Delhi Tourist Police: +91-11-23363363",
                "destinations": [
                    {"name": "Qutub Minar & Mehrauli Complex", "category": "Historical", "desc": "World's tallest brick minaret at 72.5m surrounded by medieval Indo-Islamic monuments.", "lat": 28.5244, "lng": 77.1855, "img": "https://images.unsplash.com/photo-1587474260584-136574528ed5?auto=format&fit=crop&w=600&q=80", "fee": "INR 50 / 600"},
                    {"name": "India Gate & Kartavya Path", "category": "Historical", "desc": "Iconic war memorial arch honoring 84,000 soldiers with wide tree-lined public boulevards.", "lat": 28.6129, "lng": 77.2295, "img": "https://images.unsplash.com/photo-1592635196078-9ffc7f113781?auto=format&fit=crop&w=600&q=80", "fee": "Free"}
                ]
            },
            {
                "code": "CH",
                "name": "Chandigarh",
                "category": "union_territory",
                "region": "Northern",
                "capital": "Chandigarh",
                "banner_image": "https://images.unsplash.com/photo-1622396481304-4ad7769911e8?auto=format&fit=crop&w=1200&q=80",
                "description": "The 'City Beautiful', celebrated worldwide as Le Corbusier's modern urban planning masterpiece with lush gardens and Sukhna Lake.",
                "best_season": "September to March",
                "official_website": "https://chandigarhtourism.gov.in",
                "culture_traditions": "Open hand monument philosophy, Chandigarh Rose Festival, and modern art galleries.",
                "local_food": "Tandoori Chicken, Paneer Tikka, Amritsari Naan, and Creamy Lassi.",
                "emergency_helpline": "112 / +91-172-2740420",
                "destinations": [
                    {"name": "Nek Chand's Rock Garden", "category": "Cultural", "desc": "A visionary 40-acre sculpture park crafted entirely from urban industrial and domestic waste.", "lat": 30.7525, "lng": 76.8073, "img": "https://images.unsplash.com/photo-1622396481304-4ad7769911e8?auto=format&fit=crop&w=600&q=80", "fee": "INR 30"},
                    {"name": "Sukhna Lake", "category": "Natural", "desc": "Picturesque 3 sq km artificial reservoir at the foothills of the Shivalik range offering solar boating.", "lat": 30.7421, "lng": 76.8188, "img": "https://images.unsplash.com/photo-1590417817097-474088a87754?auto=format&fit=crop&w=600&q=80", "fee": "Free / Boating extra"}
                ]
            },
            {
                "code": "LA",
                "name": "Ladakh",
                "category": "union_territory",
                "region": "Northern",
                "capital": "Leh",
                "banner_image": "https://images.unsplash.com/photo-1581793745862-99fde7fa73d2?auto=format&fit=crop&w=1200&q=80",
                "description": "The 'Land of High Passes', an awe-inspiring high-altitude desert framed by the Karakoram and Zanskar mountain ranges.",
                "best_season": "May to September",
                "official_website": "https://ladakhtourism.in",
                "culture_traditions": "Hemis monastery cham masked dance, Ladakhi Losar festival, and Buddhist prayer wheel customs.",
                "local_food": "Thukpa, Momos, Tingmo, Skyu, and salted Butter Tea (Gur Gur Chai).",
                "emergency_helpline": "112 / Leh Tourist Office: +91-1982-252297",
                "destinations": [
                    {"name": "Pangong Tso Lake", "category": "Natural", "desc": "Breathtaking endorheic lake at 4,225m changing shades of blue throughout the day.", "lat": 33.7595, "lng": 78.6674, "img": "https://images.unsplash.com/photo-1581793745862-99fde7fa73d2?auto=format&fit=crop&w=600&q=80", "fee": "Inner Line Permit required"},
                    {"name": "Nubra Valley & Khardung La", "category": "Adventure", "desc": "Cold desert sand dunes with double-humped Bactrian camels reached via high motorable passes.", "lat": 34.6863, "lng": 77.5673, "img": "https://images.unsplash.com/photo-1506197603052-3cc9c3a201bd?auto=format&fit=crop&w=600&q=80", "fee": "Permit required"}
                ]
            },

            # --- Western & Central India (6: 5 states, 1 UT) ---
            {
                "code": "GJ",
                "name": "Gujarat",
                "category": "state",
                "region": "Western/Central",
                "capital": "Gandhinagar",
                "banner_image": "https://images.unsplash.com/photo-1609137144822-263a76383637?auto=format&fit=crop&w=1200&q=80",
                "description": "Land of Legends, boasting the White Rann of Kutch, the Statue of Unity, Asiatic lions in Gir, and stepwell architecture.",
                "best_season": "November to February",
                "official_website": "https://gujarattourism.com",
                "culture_traditions": "Vibrant Garba and Dandiya Raas during Navratri, Patola silk weaving, and Rann Utsav festival.",
                "local_food": "Gujarati Thali, Dhokla, Khandvi, Thepla, Fafda-Jalebi, and Undhiyu.",
                "emergency_helpline": "112 / Tourist Helpline: 1800-200-5080",
                "destinations": [
                    {"name": "Statue of Unity, Kevadia", "category": "Historical", "desc": "World's tallest statue at 182m honoring Sardar Vallabhbhai Patel on the Narmada River.", "lat": 21.8380, "lng": 73.7191, "img": "https://images.unsplash.com/photo-1570783359008-8e6f30a91176?auto=format&fit=crop&w=600&q=80", "fee": "INR 150 - 380"},
                    {"name": "Rann of Kutch (White Desert)", "category": "Natural", "desc": "Extensive salt marsh shining like snow under full moonlight during winter Rann Utsav.", "lat": 23.7337, "lng": 69.8597, "img": "https://images.unsplash.com/photo-1609137144822-263a76383637?auto=format&fit=crop&w=600&q=80", "fee": "INR 100 (Permit)"}
                ]
            },
            {
                "code": "MH",
                "name": "Maharashtra",
                "category": "state",
                "region": "Western/Central",
                "capital": "Mumbai",
                "banner_image": "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?auto=format&fit=crop&w=1200&q=80",
                "description": "Dynamic state combining financial powerhouse Mumbai, UNESCO cave complexes of Ajanta & Ellora, and Sahyadri mountain forts.",
                "best_season": "October to March",
                "official_website": "https://maharashtratourism.gov.in",
                "culture_traditions": "Lavani dance, grand Ganesh Chaturthi festivals, and Maratha warrior heritage.",
                "local_food": "Vada Pav, Pav Bhaji, Misal Pav, Puran Poli, and Kolhapuri Mutton Rassa.",
                "emergency_helpline": "112 / Mumbai Tourist Police: +91-22-22620111",
                "destinations": [
                    {"name": "Gateway of India & Marine Drive, Mumbai", "category": "Historical", "desc": "Symbolic colonial monument facing the Arabian Sea and the curved Queen's Necklace promenade.", "lat": 18.9220, "lng": 72.8347, "img": "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?auto=format&fit=crop&w=600&q=80", "fee": "Free"},
                    {"name": "Ajanta & Ellora Caves, Chhatrapati Sambhajinagar", "category": "Historical", "desc": "30+ rock-cut Buddhist, Hindu and Jain cave temples including monolithic Kailash Temple.", "lat": 20.0268, "lng": 75.1780, "img": "https://images.unsplash.com/photo-1600100397608-f010f443b77a?auto=format&fit=crop&w=600&q=80", "fee": "INR 40 / 600"}
                ]
            },
            {
                "code": "GA",
                "name": "Goa",
                "category": "state",
                "region": "Western/Central",
                "capital": "Panaji",
                "banner_image": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=1200&q=80",
                "description": "India's premier coastal haven famous for golden sand beaches, Portuguese colonial architecture, spice plantations, and vibrant nightlife.",
                "best_season": "November to February",
                "official_website": "https://goatourism.gov.in",
                "culture_traditions": "Goa Carnival, Shigmo festival, Latin quarter fontainhas walks, and fado music.",
                "local_food": "Goan Fish Curry Rice, Pork Vindaloo, Bebinca dessert, and Feni.",
                "emergency_helpline": "112 / Goa Tourist Police: +91-832-2425112",
                "destinations": [
                    {"name": "Basilica of Bom Jesus, Old Goa", "category": "Historical", "desc": "UNESCO World Heritage 16th-century church holding the mortal remains of St. Francis Xavier.", "lat": 15.5009, "lng": 73.9116, "img": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=600&q=80", "fee": "Free"},
                    {"name": "Palolem & Agonda Beaches", "category": "Natural", "desc": "Serene crescent-shaped South Goa beaches famous for gentle surf and beach shacks.", "lat": 15.0100, "lng": 74.0232, "img": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=80", "fee": "Free"}
                ]
            },
            {
                "code": "MP",
                "name": "Madhya Pradesh",
                "category": "state",
                "region": "Western/Central",
                "capital": "Bhopal",
                "banner_image": "https://images.unsplash.com/photo-1600100397608-f010f443b77a?auto=format&fit=crop&w=1200&q=80",
                "description": "The Heart of Incredible India, celebrated for Khajuraho temples, Sanchi Stupa, and dense tiger reserves like Kanha, Bandhavgarh, and Pench.",
                "best_season": "October to March",
                "official_website": "https://mptourism.com",
                "culture_traditions": "Gond tribal painting, Chanderi and Maheshwari handloom sarees, and Dhrupad music.",
                "local_food": "Poha Jalebi, Bhutte Ka Kees, Dal Bafla, Rogan Josh, and Mawa Bati.",
                "emergency_helpline": "112 / MP Tourism: 1800-233-7777",
                "destinations": [
                    {"name": "Khajuraho Group of Monuments", "category": "Historical", "desc": "UNESCO World Heritage site noted for intricately carved Nagara-style medieval temples.", "lat": 24.8318, "lng": 79.9199, "img": "https://images.unsplash.com/photo-1600100397608-f010f443b77a?auto=format&fit=crop&w=600&q=80", "fee": "INR 40 / 600"},
                    {"name": "Bandhavgarh National Park", "category": "Natural", "desc": "One of India's highest tiger density national parks set amid ancient fortress ruins.", "lat": 23.7226, "lng": 81.0242, "img": "https://images.unsplash.com/photo-1561731216-c3a4d99437d5?auto=format&fit=crop&w=600&q=80", "fee": "INR 1500 - 6500 (Safari)"}
                ]
            },
            {
                "code": "CG",
                "name": "Chhattisgarh",
                "category": "state",
                "region": "Western/Central",
                "capital": "Raipur",
                "banner_image": "https://images.unsplash.com/photo-1518457607834-6e8d80c183c5?auto=format&fit=crop&w=1200&q=80",
                "description": "An eco-tourism treasure boasting Chitrakote 'Niagara of India' Falls, dense Sal forests of Bastar, and ancient tribal metalcraft.",
                "best_season": "October to March",
                "official_website": "https://chhattisgarhtourism.cg.gov.in",
                "culture_traditions": "Dhokra bell metal craft, Bastar Dussehra (75-day festival), and Panthi and Karma folk dances.",
                "local_food": "Chila, Faraa, Muthia, Aamat, and Mahua drink.",
                "emergency_helpline": "112 / +91-771-4040777",
                "destinations": [
                    {"name": "Chitrakote Waterfalls, Bastar", "category": "Natural", "desc": "India's widest waterfall, known as the 'Niagara of India', plunging 30 meters on the Indravati River.", "lat": 19.2016, "lng": 81.7011, "img": "https://images.unsplash.com/photo-1518457607834-6e8d80c183c5?auto=format&fit=crop&w=600&q=80", "fee": "Free"},
                    {"name": "Sirpur Heritage Complex", "category": "Historical", "desc": "Ancient 5th to 8th century archaeological Buddhist and Hindu site on the Mahanadi river.", "lat": 21.3411, "lng": 82.1794, "img": "https://images.unsplash.com/photo-1590073844006-33379778ae09?auto=format&fit=crop&w=600&q=80", "fee": "INR 25"}
                ]
            },
            {
                "code": "DNHDD",
                "name": "Dadra and Nagar Haveli and Daman and Diu",
                "category": "union_territory",
                "region": "Western/Central",
                "capital": "Daman",
                "banner_image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
                "description": "Coastal enclave featuring historic Portuguese forts, serene palm-fringed beaches, and tribal culture in Silvassa.",
                "best_season": "October to May",
                "official_website": "https://tourism.dddgov.in",
                "culture_traditions": "Portuguese Mando music, tribal Tarpa dance, and coastal fishing culture.",
                "local_food": "Fresh coastal seafood, Chicken Xacuti, Parsi Dhansak, and coconut curry.",
                "emergency_helpline": "112 / +91-260-2255104",
                "destinations": [
                    {"name": "Diu Fort & Nagoa Beach", "category": "Historical", "desc": "16th-century fortress encircled by the sea with lighthouses and semicircular horseshoe beach.", "lat": 20.7139, "lng": 70.9904, "img": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=80", "fee": "Free"},
                    {"name": "Moti Daman Fort & St. Jerome Church", "category": "Historical", "desc": "Enormous rampart fortress housing Portuguese colonial cathedrals.", "lat": 20.4146, "lng": 72.8328, "img": "https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=600&q=80", "fee": "Free"}
                ]
            },

            # --- Eastern India (6: 5 states, 1 UT) ---
            {
                "code": "BR",
                "name": "Bihar",
                "category": "state",
                "region": "Eastern",
                "capital": "Patna",
                "banner_image": "https://images.unsplash.com/photo-1590073844006-33379778ae09?auto=format&fit=crop&w=1200&q=80",
                "description": "Birthplace of Buddhism and Jainism, featuring sacred Mahabodhi Temple at Bodh Gaya and the ancient Nalanda University ruins.",
                "best_season": "October to March",
                "official_website": "https://tourism.bihar.gov.in",
                "culture_traditions": "Madhubani (Mithila) paintings, Chhath Puja grand festival, and Manjusha art.",
                "local_food": "Litti Chokha, Sattu Paratha, Thekua, Khaja, and Malpua.",
                "emergency_helpline": "112 / +91-612-2506214",
                "destinations": [
                    {"name": "Mahabodhi Temple, Bodh Gaya", "category": "Pilgrimage", "desc": "UNESCO World Heritage temple marking where Gautama Buddha attained enlightenment under the Bodhi Tree.", "lat": 24.6959, "lng": 84.9914, "img": "https://images.unsplash.com/photo-1590073844006-33379778ae09?auto=format&fit=crop&w=600&q=80", "fee": "Free"},
                    {"name": "Nalanda Mahavihara Ruins", "category": "Historical", "desc": "UNESCO site preserving the world's most acclaimed 5th-century residential monastic university.", "lat": 25.1357, "lng": 85.4439, "img": "https://images.unsplash.com/photo-1600100397608-f010f443b77a?auto=format&fit=crop&w=600&q=80", "fee": "INR 40 / 600"}
                ]
            },
            {
                "code": "JH",
                "name": "Jharkhand",
                "category": "state",
                "region": "Eastern",
                "capital": "Ranchi",
                "banner_image": "https://images.unsplash.com/photo-1518457607834-6e8d80c183c5?auto=format&fit=crop&w=1200&q=80",
                "description": "The Land of Forests (Vananchal), noted for roaring waterfalls around Ranchi, Parasnath Jain hills, and rich tribal art.",
                "best_season": "October to March",
                "official_website": "https://tourism.jharkhand.gov.in",
                "culture_traditions": "Sohrai and Khovar mural paintings, Chhau dance, and Sarhul nature festival.",
                "local_food": "Dhuska with Ghugni, Chilka Roti, Rugra curry, and Bamboo Shoot sabzi.",
                "emergency_helpline": "112 / +91-651-2400981",
                "destinations": [
                    {"name": "Hundru & Jonha Falls, Ranchi", "category": "Natural", "desc": "Spectacular cascading waterfalls over the Subarnarekha river falling 98 meters.", "lat": 23.4475, "lng": 85.6567, "img": "https://images.unsplash.com/photo-1518457607834-6e8d80c183c5?auto=format&fit=crop&w=600&q=80", "fee": "INR 20"},
                    {"name": "Betla National Park", "category": "Natural", "desc": "Palamu tiger reserve featuring elephants, bisons, and medieval Chero dynasty forts.", "lat": 23.8837, "lng": 84.1868, "img": "https://images.unsplash.com/photo-1561731216-c3a4d99437d5?auto=format&fit=crop&w=600&q=80", "fee": "INR 100"}
                ]
            },
            {
                "code": "OD",
                "name": "Odisha",
                "category": "state",
                "region": "Eastern",
                "capital": "Bhubaneswar",
                "banner_image": "https://images.unsplash.com/photo-1609137144822-263a76383637?auto=format&fit=crop&w=1200&q=80",
                "description": "Land of Jagannath Puri, Sun Temple at Konark, Asia's largest brackish lagoon Chilika Lake, and pristine silver filigree art.",
                "best_season": "October to March",
                "official_website": "https://odishatourism.gov.in",
                "culture_traditions": "Odissi classical dance, Pattachitra scroll painting, and grand Puri Jagannath Ratha Yatra.",
                "local_food": "Chhena Poda (baked cheese dessert), Dalma, Rasagola, Pakhala Bhata, and Crab Kalia.",
                "emergency_helpline": "112 / Tourist Police Puri: +91-6752-223400",
                "destinations": [
                    {"name": "Konark Sun Temple", "category": "Historical", "desc": "UNESCO World Heritage 13th-century chariot temple dedicated to Surya with 24 carved stone wheels.", "lat": 19.8876, "lng": 86.0945, "img": "https://images.unsplash.com/photo-1600100397608-f010f443b77a?auto=format&fit=crop&w=600&q=80", "fee": "INR 40 / 600"},
                    {"name": "Chilika Lake & Irrawaddy Dolphins", "category": "Natural", "desc": "Asia's largest saltwater lake home to rare Irrawaddy dolphins and millions of winter migratory birds.", "lat": 19.7042, "lng": 85.3218, "img": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=80", "fee": "Boating varies"}
                ]
            },
            {
                "code": "WB",
                "name": "West Bengal",
                "category": "state",
                "region": "Eastern",
                "capital": "Kolkata",
                "banner_image": "https://images.unsplash.com/photo-1558431382-27e303142255?auto=format&fit=crop&w=1200&q=80",
                "description": "Cultural powerhouse stretching from Darjeeling Himalayan tea hills to Sundarbans mangrove tiger swamps and artistic Kolkata.",
                "best_season": "October to March",
                "official_website": "https://wbtourism.gov.in",
                "culture_traditions": "UNESCO-inscribed Durga Puja festival, Rabindra Sangeet, Baul folk songs, and Kantha stitch craft.",
                "local_food": "Macher Jhol (Fish Curry), Kosha Mangsho, Mishti Doi, Rosogolla, and Kolkata Biryani.",
                "emergency_helpline": "112 / Kolkata Tourist Assistance: +91-33-22145858",
                "destinations": [
                    {"name": "Victoria Memorial & Howrah Bridge, Kolkata", "category": "Historical", "desc": "Stately white marble monument surrounded by 64 acres of gardens and iconic cantilever bridge.", "lat": 22.5448, "lng": 88.3426, "img": "https://images.unsplash.com/photo-1558431382-27e303142255?auto=format&fit=crop&w=600&q=80", "fee": "INR 50 / 500"},
                    {"name": "Darjeeling Himalayan Railway & Tiger Hill", "category": "Adventure", "desc": "UNESCO toy train ride with sunrise views of Mt. Kanchenjunga.", "lat": 27.0360, "lng": 88.2627, "img": "https://images.unsplash.com/photo-1605649487212-47bdab064df8?auto=format&fit=crop&w=600&q=80", "fee": "INR 1000 - 1500 (Toy Train)"}
                ]
            },
            {
                "code": "SK",
                "name": "Sikkim",
                "category": "state",
                "region": "Eastern",
                "capital": "Gangtok",
                "banner_image": "https://images.unsplash.com/photo-1589182373726-e4f658ab50f0?auto=format&fit=crop&w=1200&q=80",
                "description": "India's first 100% organic state, framed by majestic Mount Kanchenjunga, alpine meadows of Yumthang, and ancient Rumtek Monastery.",
                "best_season": "March to May, October to mid-December",
                "official_website": "https://sikkimtourism.gov.in",
                "culture_traditions": "Lepcha, Bhutia and Nepali heritage, masked monastery dances (Chaam), and Thangka painting.",
                "local_food": "Momos, Thukpa, Gundruk, Phagshapa, Kinema curry, and Chhurpi soup.",
                "emergency_helpline": "112 / Sikkim Tourist Police: +91-3592-209090",
                "destinations": [
                    {"name": "Tsomgo Lake & Nathu La Pass", "category": "Natural", "desc": "Glacial lake at 3,753m sacred to locals and historic Silk Road border pass.", "lat": 27.3742, "lng": 88.7619, "img": "https://images.unsplash.com/photo-1589182373726-e4f658ab50f0?auto=format&fit=crop&w=600&q=80", "fee": "Permit required"},
                    {"name": "Gurudongmar Lake, North Sikkim", "category": "Adventure", "desc": "One of the highest lakes in the world at 5,430m revered by Buddhists, Sikhs, and Hindus.", "lat": 28.0258, "lng": 88.7099, "img": "https://images.unsplash.com/photo-1506197603052-3cc9c3a201bd?auto=format&fit=crop&w=600&q=80", "fee": "Permit required"}
                ]
            },
            {
                "code": "AN",
                "name": "Andaman and Nicobar Islands",
                "category": "union_territory",
                "region": "Eastern",
                "capital": "Port Blair",
                "banner_image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
                "description": "Tropical archipelago in the Bay of Bengal, famous for Radhanagar Beach, scuba diving coral reefs, and the historic Cellular Jail.",
                "best_season": "October to May",
                "official_website": "https://www.andamantourism.gov.in",
                "culture_traditions": "Indigenous tribal conservation, island boat regattas, and solemn freedom fighter memorials.",
                "local_food": "Fresh Lobster, Crab curry, grilled Snapper, Coconut prawn curry, and tropical fruit platters.",
                "emergency_helpline": "112 / Tourist Police Port Blair: +91-3192-232100",
                "destinations": [
                    {"name": "Radhanagar Beach, Havelock (Swaraj Dweep)", "category": "Natural", "desc": "Consistently ranked among Asia's top beaches for turquoise waters and white silica sands.", "lat": 11.9840, "lng": 92.9515, "img": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=80", "fee": "Free"},
                    {"name": "Cellular Jail National Memorial, Port Blair", "category": "Historical", "desc": "Colonial prison synonymous with India's freedom struggle featuring poignant Sound & Light show.", "lat": 11.6739, "lng": 92.7478, "img": "https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=600&q=80", "fee": "INR 30 / 150 (Show)"}
                ]
            },

            # --- Southern India (7: 5 states, 2 UTs) ---
            {
                "code": "AP",
                "name": "Andhra Pradesh",
                "category": "state",
                "region": "Southern",
                "capital": "Amaravati",
                "banner_image": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1200&q=80",
                "description": "Endowed with sacred Tirupati Venkateswara Temple, scenic Araku Valley, Borra Caves, and India's second-longest coastline.",
                "best_season": "October to March",
                "official_website": "https://tourism.ap.gov.in",
                "culture_traditions": "Kuchipudi classical dance, Kalamkari hand-painted textiles, and Kondapalli wooden toys.",
                "local_food": "Hyderabadi/Andhra Spicy Biryani, Gongura Pachadi, Pesarattu, and Pootharekulu sweet.",
                "emergency_helpline": "112 / Tourist Police: 1800-425-45454",
                "destinations": [
                    {"name": "Tirumala Venkateswara Temple, Tirupati", "category": "Pilgrimage", "desc": "One of the most visited and revered Vaishnavite pilgrimage temples in the world.", "lat": 13.6833, "lng": 79.3472, "img": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=600&q=80", "fee": "Free / Special Darshan INR 300"},
                    {"name": "Araku Valley & Borra Caves", "category": "Natural", "desc": "Lush coffee plantations in Eastern Ghats and million-year-old limestone stalactite caves.", "lat": 18.3273, "lng": 82.8775, "img": "https://images.unsplash.com/photo-1518457607834-6e8d80c183c5?auto=format&fit=crop&w=600&q=80", "fee": "INR 80"}
                ]
            },
            {
                "code": "TG",
                "name": "Telangana",
                "category": "state",
                "region": "Southern",
                "capital": "Hyderabad",
                "banner_image": "https://images.unsplash.com/photo-1605649487212-47bdab064df8?auto=format&fit=crop&w=1200&q=80",
                "description": "Blends Nizami grandeur with high-tech momentum, featuring Charminar, Golconda Fort, Ramappa Temple, and world-famous biryani.",
                "best_season": "October to March",
                "official_website": "https://tourism.telangana.gov.in",
                "culture_traditions": "Bathukamma floral festival, Bonalu, Bidri silverware craft, and Pochampally Ikat weaving.",
                "local_food": "Hyderabadi Dum Biryani, Haleem, Mirchi ka Salan, Double ka Meetha, and Irani Chai.",
                "emergency_helpline": "112 / +91-40-23450444",
                "destinations": [
                    {"name": "Charminar & Golconda Fort, Hyderabad", "category": "Historical", "desc": "Iconic 1591 monument with four minarets and diamond fortress with acoustic marvels.", "lat": 17.3616, "lng": 78.4747, "img": "https://images.unsplash.com/photo-1605649487212-47bdab064df8?auto=format&fit=crop&w=600&q=80", "fee": "INR 25 / 300"},
                    {"name": "Ramappa Temple, Palampet", "category": "Historical", "desc": "UNESCO World Heritage 13th-century Kakatiya temple built with floating bricks.", "lat": 18.2612, "lng": 79.9419, "img": "https://images.unsplash.com/photo-1600100397608-f010f443b77a?auto=format&fit=crop&w=600&q=80", "fee": "INR 40"}
                ]
            },
            {
                "code": "KA",
                "name": "Karnataka",
                "category": "state",
                "region": "Southern",
                "capital": "Bengaluru",
                "banner_image": "https://images.unsplash.com/photo-1600100397608-f010f443b77a?auto=format&fit=crop&w=1200&q=80",
                "description": "One State, Many Worlds: ruins of the Vijayanagara Empire at Hampi, royal Mysore Palace, Coorg coffee hills, and tech capital Bengaluru.",
                "best_season": "October to March",
                "official_website": "https://karnatakatourism.org",
                "culture_traditions": "Yakshagana dance-drama, Mysore Dasara jumbo procession, and Bidriware and sandalwood crafts.",
                "local_food": "Bisi Bele Bath, Mysore Pak, Benne Dosa, Mangalorean Ghee Roast, and filter coffee.",
                "emergency_helpline": "112 / Karnataka Tourist Helpline: 1800-425-7878",
                "destinations": [
                    {"name": "Hampi UNESCO Ruins", "category": "Historical", "desc": "Enchanting boulder-strewn capital of the 14th-century Vijayanagara Empire with stone chariot.", "lat": 15.3350, "lng": 76.4600, "img": "https://images.unsplash.com/photo-1600100397608-f010f443b77a?auto=format&fit=crop&w=600&q=80", "fee": "INR 40 / 600"},
                    {"name": "Mysore Palace (Amba Vilas)", "category": "Historical", "desc": "Indo-Saracenic royal palace illuminated by over 100,000 bulbs on Sundays and festivals.", "lat": 12.3052, "lng": 76.6552, "img": "https://images.unsplash.com/photo-1599661046289-e31897846e41?auto=format&fit=crop&w=600&q=80", "fee": "INR 100 / 300"}
                ]
            },
            {
                "code": "KL",
                "name": "Kerala",
                "category": "state",
                "region": "Southern",
                "capital": "Thiruvananthapuram",
                "banner_image": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=1200&q=80",
                "description": "God's Own Country, famed for tranquil Alleppey backwaters, Munnar tea hills, Ayurvedic wellness, and spice-scented coastal towns.",
                "best_season": "September to March",
                "official_website": "https://keralatourism.org",
                "culture_traditions": "Kathakali dance-theatre, Kalaripayattu martial arts, Theyyam ritual performances, and Onam boat races.",
                "local_food": "Appam with Ishtu, Karimeen Pollichathu, Kerala Sadya, Malabar Parotta with Beef/Chicken fry, and Puttu.",
                "emergency_helpline": "112 / Tourist Police Kerala: 1800-425-4747",
                "destinations": [
                    {"name": "Alleppey (Alappuzha) Backwaters", "category": "Natural", "desc": "Serene network of interconnected canals and lagoons explored on traditional Kettuvallam houseboats.", "lat": 9.4981, "lng": 76.3388, "img": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=600&q=80", "fee": "Houseboat INR 6000 - 15000/day"},
                    {"name": "Munnar Tea Plantations", "category": "Natural", "desc": "Rolling mist-covered emerald green tea estates, waterfalls, and Anamudi peak.", "lat": 10.0889, "lng": 77.0595, "img": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=600&q=80", "fee": "Free / Factory tours INR 150"}
                ]
            },
            {
                "code": "TN",
                "name": "Tamil Nadu",
                "category": "state",
                "region": "Southern",
                "capital": "Chennai",
                "banner_image": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1200&q=80",
                "description": "Land of Temples, celebrated for soaring Dravidian gopurams of Madurai, Shore Temple at Mahabalipuram, Nilgiri toy train, and Chettinad heritage.",
                "best_season": "November to February",
                "official_website": "https://tamilnadutourism.tn.gov.in",
                "culture_traditions": "Bharatanatyam classical dance, Carnatic music Margazhi season, Tanjore paintings, and Kanchipuram silk.",
                "local_food": "Idli Sambar, Medu Vada, Chettinad Chicken, Dosa, Jigarthanda of Madurai, and filter coffee.",
                "emergency_helpline": "112 / Tamil Nadu Tourist Police: +91-44-25383333",
                "destinations": [
                    {"name": "Meenakshi Amman Temple, Madurai", "category": "Pilgrimage", "desc": "Architectural marvel with 14 colorful carved gopuram towers dedicated to Parvati and Shiva.", "lat": 9.9195, "lng": 78.1193, "img": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=600&q=80", "fee": "Free"},
                    {"name": "Mahabalipuram UNESCO Monuments", "category": "Historical", "desc": "7th-century Pallava coastal monuments including Pancha Rathas and rock-relief Arjuna's Penance.", "lat": 12.6269, "lng": 80.1927, "img": "https://images.unsplash.com/photo-1600100397608-f010f443b77a?auto=format&fit=crop&w=600&q=80", "fee": "INR 40 / 600"}
                ]
            },
            {
                "code": "PY",
                "name": "Puducherry",
                "category": "union_territory",
                "region": "Southern",
                "capital": "Pondicherry",
                "banner_image": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1200&q=80",
                "description": "The French Riviera of the East, boasting mustard-yellow colonial villas, tranquil Promenade Beach, and experimental community Auroville.",
                "best_season": "October to March",
                "official_website": "https://pondytourism.in",
                "culture_traditions": "Franco-Tamil architectural synthesis, Auroville Matrimandir meditation, and bohemian beach lifestyle.",
                "local_food": "French Baguettes, Crepes, Ratatouille, Pondicherry Fish Curry, and filter coffee.",
                "emergency_helpline": "112 / Tourist Police: +91-413-2224000",
                "destinations": [
                    {"name": "White Town (French Quarter) & Promenade", "category": "Cultural", "desc": "Colonial lanes draped in bougainvillea with French cafes, boutique hotels, and oceanfront promenade.", "lat": 11.9338, "lng": 79.8358, "img": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=600&q=80", "fee": "Free"},
                    {"name": "Auroville & Matrimandir", "category": "Cultural", "desc": "Universal township dedicated to human unity featuring golden geodesic spherical meditation sanctuary.", "lat": 12.0069, "lng": 79.8105, "img": "https://images.unsplash.com/photo-1590073844006-33379778ae09?auto=format&fit=crop&w=600&q=80", "fee": "Free (Pass required for inner chamber)"}
                ]
            },
            {
                "code": "LD",
                "name": "Lakshadweep",
                "category": "union_territory",
                "region": "Southern",
                "capital": "Kavaratti",
                "banner_image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
                "description": "An archipelago of 36 coral atolls and turquoise lagoons in the Arabian Sea, offering untouched diving reefs and tranquil eco-resorts.",
                "best_season": "October to mid-May",
                "official_website": "https://lakshadweeptourism.gov.in",
                "culture_traditions": "Kolkali and Parichakali folk dances, coir rope making, and peaceful island community lifestyle.",
                "local_food": "Tuna fish curries, Rayereha (spiced red tuna), Coconut rice, and Kadalakka.",
                "emergency_helpline": "112 / +91-4896-262222",
                "destinations": [
                    {"name": "Bangaram Atoll & Lagoon", "category": "Natural", "desc": "Tear-drop shaped uninhabited coral island ringed by luminous crystal turquoise lagoon.", "lat": 10.9419, "lng": 72.2906, "img": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=80", "fee": "Permit & Package required"},
                    {"name": "Agatti Island Marine Reserve", "category": "Adventure", "desc": "Gateway island with landing strip between coral reef lagoons, offering scuba diving and glass-bottom boats.", "lat": 10.8533, "lng": 72.1930, "img": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=600&q=80", "fee": "Permit required"}
                ]
            },

            # --- Northeastern India (7: 7 states) ---
            {
                "code": "AS",
                "name": "Assam",
                "category": "state",
                "region": "Northeastern",
                "capital": "Dispur",
                "banner_image": "https://images.unsplash.com/photo-1561731216-c3a4d99437d5?auto=format&fit=crop&w=1200&q=80",
                "description": "Gateway to the Northeast, renowned for one-horned rhinos in Kaziranga, the mighty Brahmaputra river, and world-famous Assam tea estates.",
                "best_season": "November to April",
                "official_website": "https://tourism.assam.gov.in",
                "culture_traditions": "Bihu festival folk dance, Muga golden silk weaving, and Majuli Vaishnavite Satras.",
                "local_food": "Khaar, Masor Tenga (sour fish curry), Duck with Ash Gourd, Pitha sweets, and Assam CTC tea.",
                "emergency_helpline": "112 / Assam Tourist Police: +91-361-2547102",
                "destinations": [
                    {"name": "Kaziranga National Park", "category": "Natural", "desc": "UNESCO World Heritage park hosting two-thirds of the world's great one-horned rhinoceros population.", "lat": 26.5775, "lng": 93.1711, "img": "https://images.unsplash.com/photo-1561731216-c3a4d99437d5?auto=format&fit=crop&w=600&q=80", "fee": "INR 100 / Safari extra"},
                    {"name": "Kamakhya Temple, Guwahati", "category": "Pilgrimage", "desc": "One of the oldest and most revered Shakti Peethas perched on Nilachal Hill overlooking the Brahmaputra.", "lat": 26.1664, "lng": 91.7058, "img": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=600&q=80", "fee": "Free"}
                ]
            },
            {
                "code": "AR",
                "name": "Arunachal Pradesh",
                "category": "state",
                "region": "Northeastern",
                "capital": "Itanagar",
                "banner_image": "https://images.unsplash.com/photo-1589182373726-e4f658ab50f0?auto=format&fit=crop&w=1200&q=80",
                "description": "The 'Land of the Dawn-Lit Mountains', sheltering the majestic Tawang Monastery at 3,048m, Ziro music valley, and Sela Pass.",
                "best_season": "October to April",
                "official_website": "https://arunachaltourism.com",
                "culture_traditions": "Monpa Buddhist rituals, Apatani bamboo architecture, Losar festival, and vibrant beaded jewelry.",
                "local_food": "Thukpa, Pika Pila (bamboo shoot pickle), Lukter (dried beef/pork), and Apong rice beer.",
                "emergency_helpline": "112 / Inner Line Permit: 0360-2212399",
                "destinations": [
                    {"name": "Tawang Monastery", "category": "Cultural", "desc": "India's largest monastery and second largest in the world, founded in 1680 overlooking the Tawang valley.", "lat": 27.5861, "lng": 91.8594, "img": "https://images.unsplash.com/photo-1589182373726-e4f658ab50f0?auto=format&fit=crop&w=600&q=80", "fee": "Free (ILP required)"},
                    {"name": "Ziro Valley & Sela Pass", "category": "Natural", "desc": "UNESCO tentative valley home to the Apatani tribe and high-altitude alpine pass at 4,170m.", "lat": 27.5385, "lng": 93.8340, "img": "https://images.unsplash.com/photo-1506197603052-3cc9c3a201bd?auto=format&fit=crop&w=600&q=80", "fee": "Free (ILP required)"}
                ]
            },
            {
                "code": "ML",
                "name": "Meghalaya",
                "category": "state",
                "region": "Northeastern",
                "capital": "Shillong",
                "banner_image": "https://images.unsplash.com/photo-1518457607834-6e8d80c183c5?auto=format&fit=crop&w=1200&q=80",
                "description": "The 'Abode of Clouds', famed for living root bridges of Cherrapunji, crystal clear waters of Dawki Umngot river, and Nohkalikai Falls.",
                "best_season": "September to May",
                "official_website": "https://meghalayatourism.in",
                "culture_traditions": "Matrilineal Khasi and Garo societal structure, Shad Suk Mynsiem festival, and bamboo architecture.",
                "local_food": "Jadoh (rice cooked with meat), Doh-neiiong (pork with black sesame), Tungrymbai, and Pumaloi.",
                "emergency_helpline": "112 / Meghalaya Tourism: 1800-345-3644",
                "destinations": [
                    {"name": "Double Decker Living Root Bridge, Nongriat", "category": "Adventure", "desc": "Botanical engineering marvel bio-crafted from living Ficus elastica tree roots over centuries.", "lat": 25.2505, "lng": 91.6702, "img": "https://images.unsplash.com/photo-1518457607834-6e8d80c183c5?auto=format&fit=crop&w=600&q=80", "fee": "INR 50"},
                    {"name": "Dawki Umngot River (Crystal Clear Waters)", "category": "Natural", "desc": "Glass-like river near Bangladesh border where wooden boats appear to float on air.", "lat": 25.1873, "lng": 92.0199, "img": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=80", "fee": "Boating INR 500-1000"}
                ]
            },
            {
                "code": "MN",
                "name": "Manipur",
                "category": "state",
                "region": "Northeastern",
                "capital": "Imphal",
                "banner_image": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=1200&q=80",
                "description": "Jeweled land celebrated for freshwater Loktak Lake with floating phumdis, the endangered Sangai dancing deer, and polo origins.",
                "best_season": "October to March",
                "official_website": "https://manipurtourism.gov.in",
                "culture_traditions": "Manipuri Raas Leela classical dance, Thang-Ta martial arts, and Ima Keithel (all-women market).",
                "local_food": "Kangshoi (vegetable stew), Eromba (boiled veggies with fermented fish), Singju salad, and Chak-hao Kheer.",
                "emergency_helpline": "112 / +91-385-2451368",
                "destinations": [
                    {"name": "Loktak Lake & Keibul Lamjao National Park", "category": "Natural", "desc": "World's only floating national park famous for circular organic islands (phumdis) and Sangai deer.", "lat": 24.5500, "lng": 93.8167, "img": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=600&q=80", "fee": "INR 50"},
                    {"name": "Ima Keithel (Mother's Market), Imphal", "category": "Cultural", "desc": "500-year-old historic market operated solely by over 5,000 women traders.", "lat": 24.8080, "lng": 93.9355, "img": "https://images.unsplash.com/photo-1558431382-27e303142255?auto=format&fit=crop&w=600&q=80", "fee": "Free"}
                ]
            },
            {
                "code": "MZ",
                "name": "Mizoram",
                "category": "state",
                "region": "Northeastern",
                "capital": "Aizawl",
                "banner_image": "https://images.unsplash.com/photo-1506197603052-3cc9c3a201bd?auto=format&fit=crop&w=1200&q=80",
                "description": "The Land of the Hill People, known for scenic rolling emerald hills of Aizawl, tranquil Tamdil lake, and vibrant bamboo dance.",
                "best_season": "October to March",
                "official_website": "https://tourism.mizoram.gov.in",
                "culture_traditions": "Cheraw (bamboo dance), Chapchar Kut spring festival, and exquisite handwoven Puan textiles.",
                "local_food": "Bai (steamed vegetables with pork and bamboo shoot), Vawksa Rep (smoked pork), and Sawhchiar porridge.",
                "emergency_helpline": "112 / +91-389-2333475",
                "destinations": [
                    {"name": "Reiek Tlang & Heritage Village", "category": "Natural", "desc": "Breathtaking mountain cliff viewpoint at 1,548m showcasing panoramic views of Bangladesh plains.", "lat": 23.6874, "lng": 92.6074, "img": "https://images.unsplash.com/photo-1506197603052-3cc9c3a201bd?auto=format&fit=crop&w=600&q=80", "fee": "INR 20"},
                    {"name": "Vantawng Falls", "category": "Natural", "desc": "Highest uninterrupted waterfall in Mizoram tumbling 229 meters through thick bamboo forests.", "lat": 23.2872, "lng": 92.8361, "img": "https://images.unsplash.com/photo-1518457607834-6e8d80c183c5?auto=format&fit=crop&w=600&q=80", "fee": "Free"}
                ]
            },
            {
                "code": "NL",
                "name": "Nagaland",
                "category": "state",
                "region": "Northeastern",
                "capital": "Kohima",
                "banner_image": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=1200&q=80",
                "description": "Land of Festivals, celebrated worldwide for the spectacular Hornbill Festival, Dzukou Valley of Flowers, and vibrant indigenous tribes.",
                "best_season": "October to May (Hornbill Festival in Dec)",
                "official_website": "https://tourism.nagaland.gov.in",
                "culture_traditions": "Hornbill Festival (Dec 1-10) uniting 16 tribes, warrior folk music, wood carving, and traditional shawls.",
                "local_food": "Smoked Pork with Axone (fermented soya), Bamboo shoot fish curry, and Raja Mircha (Bhut Jolokia) chutneys.",
                "emergency_helpline": "112 / Nagaland Tourist Police: +91-370-2270107",
                "destinations": [
                    {"name": "Kisama Heritage Village (Hornbill Festival)", "category": "Cultural", "desc": "Traditional village amphitheater where all major Naga tribes showcase authentic traditions every December.", "lat": 25.6033, "lng": 94.1167, "img": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=600&q=80", "fee": "INR 50 / 100 during festival"},
                    {"name": "Dzukou Valley Trek", "category": "Adventure", "desc": "Pristine emerald trekking valley at 2,452m famed for endemic Dzukou lilies and rolling green contours.", "lat": 25.5683, "lng": 94.0622, "img": "https://images.unsplash.com/photo-1506197603052-3cc9c3a201bd?auto=format&fit=crop&w=600&q=80", "fee": "INR 100 entry fee"}
                ]
            },
            {
                "code": "TR",
                "name": "Tripura",
                "category": "state",
                "region": "Northeastern",
                "capital": "Agartala",
                "banner_image": "https://images.unsplash.com/photo-1599661046289-e31897846e41?auto=format&fit=crop&w=1200&q=80",
                "description": "State of royal heritage featuring water palace Neermahal, white marble Ujjayanta Palace, and massive ancient rock carvings at Unakoti.",
                "best_season": "October to March",
                "official_website": "https://tripuratourism.gov.in",
                "culture_traditions": "Hojagiri folk acrobat dance of the Reang tribe, bamboo and cane handicrafts, and Garia Puja.",
                "local_food": "Mui Borok (berma fermented fish), Mosdeng Serma (tomato chutney), Chakhwi, and Bangui rice.",
                "emergency_helpline": "112 / +91-381-2325930",
                "destinations": [
                    {"name": "Neermahal Water Palace, Melaghar", "category": "Historical", "desc": "North East's sole water palace built in 1930 in the middle of Rudrasagar Lake.", "lat": 23.4975, "lng": 91.3186, "img": "https://images.unsplash.com/photo-1599661046289-e31897846e41?auto=format&fit=crop&w=600&q=80", "fee": "INR 30 / Boating INR 100"},
                    {"name": "Unakoti Rock-Cut Carvings", "category": "Historical", "desc": "Ancient Shaivite rock relief sculptures carved into mountain cliffs dating back to the 7th-9th century.", "lat": 24.3211, "lng": 92.0522, "img": "https://images.unsplash.com/photo-1600100397608-f010f443b77a?auto=format&fit=crop&w=600&q=80", "fee": "Free"}
                ]
            }
        ]

        # Insert States and Destinations
        for s_data in states_data:
            banner_image = STATE_BANNERS.get(s_data["code"], s_data["banner_image"])
            state_obj = models.StateUT(
                code=s_data["code"],
                name=s_data["name"],
                category=s_data["category"],
                region=s_data["region"],
                capital=s_data["capital"],
                banner_image=banner_image,
                description=s_data["description"],
                best_season=s_data["best_season"],
                official_website=s_data["official_website"],
                culture_traditions=s_data["culture_traditions"],
                local_food=s_data["local_food"],
                emergency_helpline=s_data["emergency_helpline"]
            )
            db.add(state_obj)
            db.flush()

            for d in s_data.get("destinations", []):
                dest_obj = models.Destination(
                    state_id=state_obj.id,
                    name=d["name"],
                    category=d["category"],
                    description=d["desc"],
                    latitude=d["lat"],
                    longitude=d["lng"],
                    image_url=d["img"],
                    entry_fee=d["fee"],
                    safety_score=4.9,
                    is_featured=True
                )
                db.add(dest_obj)

        db.flush()

        # 3. Seed Local Authorities
        dl_state = db.query(models.StateUT).filter_by(code="DL").first()
        rj_state = db.query(models.StateUT).filter_by(code="RJ").first()
        ga_state = db.query(models.StateUT).filter_by(code="GA").first()
        uk_state = db.query(models.StateUT).filter_by(code="UK").first()
        kl_state = db.query(models.StateUT).filter_by(code="KL").first()

        authorities_data = [
            {"state_id": dl_state.id, "name": "Delhi Tourist Police Central Unit", "category": "tourist_police", "phone": "+91-11-23363363", "address": "Janpath, Connaught Place, New Delhi", "latitude": 28.6270, "longitude": 77.2180, "is_emergency": True},
            {"state_id": dl_state.id, "name": "AIIMS New Delhi Emergency Trauma Centre", "category": "hospital", "phone": "102 / +91-11-26588500", "address": "Sri Aurobindo Marg, Ansari Nagar, New Delhi", "latitude": 28.5672, "longitude": 77.2100, "is_emergency": True},
            {"state_id": rj_state.id, "name": "Jaipur Tourist Assistance Police Outpost", "category": "tourist_police", "phone": "+91-141-2822830", "address": "MI Road, Ajmeri Gate, Jaipur", "latitude": 26.9180, "longitude": 75.8190, "is_emergency": True},
            {"state_id": rj_state.id, "name": "SMS Hospital Jaipur (Govt Emergency)", "category": "hospital", "phone": "+91-141-2560291", "address": "JLN Marg, Ashok Nagar, Jaipur", "latitude": 26.8980, "longitude": 75.8150, "is_emergency": True},
            {"state_id": ga_state.id, "name": "Goa Coastal & Beach Police Station", "category": "police", "phone": "+91-832-2425112", "address": "Calangute Beach Promenade, North Goa", "latitude": 15.5430, "longitude": 73.7550, "is_emergency": True},
            {"state_id": ga_state.id, "name": "Goa Medical College & Hospital (Bambolim)", "category": "hospital", "phone": "108 / +91-832-2458700", "address": "NH 66, Bambolim, Goa", "latitude": 15.4600, "longitude": 73.8560, "is_emergency": True},
            {"state_id": uk_state.id, "name": "SDRF Disaster Management & River Rescue Cell", "category": "disaster", "phone": "1070 / +91-135-2710334", "address": "Triveni Ghat, Rishikesh, Uttarakhand", "latitude": 30.1030, "longitude": 78.2930, "is_emergency": True},
            {"state_id": kl_state.id, "name": "Alleppey Boat Safety & Tourist Police Unit", "category": "tourist_police", "phone": "+91-477-2251786", "address": "Finishing Point Jetty, Alappuzha, Kerala", "latitude": 9.4920, "longitude": 76.3420, "is_emergency": True}
        ]

        for auth in authorities_data:
            db.add(models.LocalAuthority(**auth))

        # 4. Seed Geofences (Safe Zones, Hazards, Restricted Areas)
        geofences_data = [
            {
                "state_id": dl_state.id,
                "name": "Connaught Place Safe Tourism Zone",
                "zone_type": "tourist_safety",
                "description": "Pedestrian friendly, heavy police patrols, high density of help desks and certified outlets.",
                "center_latitude": 28.6315,
                "center_longitude": 77.2167,
                "radius_meters": 1200.0,
                "warning_message": "You are inside a verified Safe Tourist Zone with 24x7 Tourist Police presence."
            },
            {
                "state_id": dl_state.id,
                "name": "Asola Bhatti Wildlife Sanctuary Buffer Alert",
                "zone_type": "restricted",
                "description": "Restricted forestry boundary after dusk. Steep quarry pits and wild animal crossings.",
                "center_latitude": 28.4850,
                "center_longitude": 77.2340,
                "radius_meters": 1800.0,
                "warning_message": "Warning: You have approached a protected wildlife sanctuary with restricted entry. Please stay on marked trails."
            },
            {
                "state_id": rj_state.id,
                "name": "Jaipur Walled City Heritage Safe Corridor",
                "zone_type": "tourist_safety",
                "description": "Hawa Mahal & City Palace pedestrian corridor with continuous tourist assistance.",
                "center_latitude": 26.9240,
                "center_longitude": 75.8267,
                "radius_meters": 1500.0,
                "warning_message": "Verified Safe Tourist Walkway: Official government tourist guides and CCTV surveillance active."
            },
            {
                "state_id": ga_state.id,
                "name": "Baga Creek Rip-Current Danger Hazard",
                "zone_type": "hazard",
                "description": "Dangerous strong underwater undertow during mid-tide and monsoon seasons.",
                "center_latitude": 15.5560,
                "center_longitude": 73.7510,
                "radius_meters": 600.0,
                "warning_message": "Hazard Alert: High rip currents reported in this coastal stretch. Swimming is strictly prohibited!"
            },
            {
                "state_id": uk_state.id,
                "name": "Shivpuri Rapid Rock Cliff Zone",
                "zone_type": "hazard",
                "description": "Steep rocky river embankment along the Ganges. Slippery rocks and rapid water currents.",
                "center_latitude": 30.1360,
                "center_longitude": 78.3880,
                "radius_meters": 800.0,
                "warning_message": "Caution: Dangerous river rapids and slippery cliffs. Life jackets mandatory by order of SDRF."
            }
        ]

        for gf in geofences_data:
            db.add(models.Geofence(**gf))

        # 5. Seed 13 Comprehensive Safety Protocols
        protocols_data = [
            {
                "category": "General Tourist Safety",
                "title": "Essential Travel Safety Guidelines for India",
                "summary": "Core guidelines for domestic and international travelers exploring Indian cities and rural regions.",
                "warning_signs": "Unlicensed guides approaching at transport hubs; insistence on cash payments without receipts; taxis refusing to use meters or certified apps.",
                "dos": "Keep emergency contacts updated; use certified prepaid taxis or ride-hailing apps; carry bottled drinking water; keep photocopies of passport and ID.",
                "donts": "Do not accept food or unwrapped beverages from strangers; do not flash large stacks of cash in crowded bazaars; avoid unlit isolated alleys at night.",
                "emergency_guidance": "Dial 112 nationwide for any emergency or press the Geonova SOS button for instant assistance.",
                "icon_name": "shield"
            },
            {
                "category": "Solo Travel Safety",
                "title": "Smart Protocols for Solo Backpackers",
                "summary": "Proven methods to stay safe, secure your belongings, and navigate India with confidence as a solo traveler.",
                "warning_signs": "Strangers asking overly specific questions about your hotel room or solo travel itinerary; unsolicited offers for free private tours.",
                "dos": "Share your live trip tracking with a trusted family member; book verified accommodations with verified reviews; arrive at new destinations during daylight hours.",
                "donts": "Do not leave drinks unattended in social bars; do not hitchhike in unverified vehicles.",
                "emergency_guidance": "In an uncomfortable situation, head to the nearest hotel lobby, railway assistance counter, or dial 112.",
                "icon_name": "user"
            },
            {
                "category": "Women's Safety",
                "title": "Women Travelers Safety Shield & Resources",
                "summary": "Specialized measures, dedicated helplines, safe public transit spaces, and accommodation verification for female travelers.",
                "warning_signs": "Persistent following or uninvited photographing; uncertified drivers claiming their company sent them.",
                "dos": "Use women-only metro coaches (front coach in Delhi Metro); utilize Women Police Helpline 1090 or 181; choose hotels with 24/7 security desks.",
                "donts": "Do not share exact room numbers aloud at reception counters; avoid travelling in empty local buses late at night.",
                "emergency_guidance": "Dial 1090 (Women Power Line) or 181 (Women in Distress Helpline) or 112 immediately. The Geonova SOS will trigger high-priority alerts.",
                "icon_name": "heart"
            },
            {
                "category": "Child and Family Travel Safety",
                "title": "Safety Protocols for Families with Children",
                "summary": "Protecting young children in bustling tourist attractions, theme parks, religious festivals, and transit hubs.",
                "warning_signs": "Crowded religious processions or train stations where visual contact can be easily severed.",
                "dos": "Put an emergency ID wristband with parent's phone number on each child; snap a daily photo of children to record what they are wearing; carry family first-aid kits.",
                "donts": "Never leave young children unattended near hotel swimming pools, open water bodies, or bustling market crossroads.",
                "emergency_guidance": "If a child is separated, immediately notify the nearest tourist police post, station master, or dial Childline 1098 / 112.",
                "icon_name": "users"
            },
            {
                "category": "Mountain and Trekking Safety",
                "title": "High Altitude & Himalayan Expedition Guidelines",
                "summary": "Crucial protocols for Ladakh, Himachal, Uttarakhand, and Sikkim high-altitude treks above 2,500 meters.",
                "warning_signs": "Persistent headache, dizziness, nausea, shortness of breath at rest (signs of Acute Mountain Sickness - AMS).",
                "dos": "Acclimatize for at least 48 hours upon arriving in Leh or high-altitude stations; stay well hydrated; hire certified IMF or state-registered mountain guides.",
                "donts": "Never ignore AMS symptoms or ascend further when feeling unwell; do not hike alone on unmarked glacial terrain.",
                "emergency_guidance": "Descend immediately to a lower altitude if symptoms worsen. Dial SDRF / ITBP mountain rescue through 112.",
                "icon_name": "mountain"
            },
            {
                "category": "Coastal and Water-Activity Safety",
                "title": "Beach, Snorkeling and Scuba Safety Measures",
                "summary": "Ocean current safety in Goa, Kerala, Andaman, and coastal Tamil Nadu waters.",
                "warning_signs": "Red beach flags hoisted by lifeguards; discolored choppy water channels indicating rip currents.",
                "dos": "Swim only between the red and yellow flags where Drishti/official lifeguards are posted; wear certified lifejackets on all boat and watersport rides.",
                "donts": "Never swim after consuming alcohol; avoid swimming in the sea during the monsoon season (June - August).",
                "emergency_guidance": "If caught in a rip current, remain calm, do not swim against it; swim parallel to the shoreline until free. Alert beach lifeguards or call 112.",
                "icon_name": "anchor"
            },
            {
                "category": "Wildlife and Forest Safety",
                "title": "National Park Safari & Wildlife Encounters",
                "summary": "Rules for wildlife safaris in Corbett, Kaziranga, Ranthambore, Gir, and Kanha national parks.",
                "warning_signs": "Animal agitation signs (ears pinned back, trumpeting elephants, tail swishing).",
                "dos": "Always stay inside your authorized gypsy or canter; maintain complete silence near wildlife; obey forest ranger instructions.",
                "donts": "Never get down from safari vehicles; never offer food to wild animals; no flash photography or drone flying.",
                "emergency_guidance": "In case of vehicle breakdown, stay seated calmly inside the vehicle while your forest guide calls base camp via wireless radio.",
                "icon_name": "tree"
            },
            {
                "category": "Mining-Area and Industrial-Zone Safety",
                "title": "Protocols for Transit Near Mining and Heavy Industry",
                "summary": "Precautions when traveling through mineral belts, stone quarry regions, or industrial transit corridors.",
                "warning_signs": "Heavy dumper traffic, warning signs of active blasting, particulate dust clouds, unmarked deep excavations.",
                "dos": "Keep vehicle windows closed in quarry zones; observe all high-visibility speed limit signage; yield right of way to heavy haulage trucks.",
                "donts": "Do not enter unauthorized private quarry pits or disused open cast mines; avoid nighttime driving on unlit mineral haul roads.",
                "emergency_guidance": "Contact local highway patrol on 112 or local district administration in the event of an obstruction or chemical spill.",
                "icon_name": "alert-triangle"
            },
            {
                "category": "Road and Driving Safety",
                "title": "Self-Drive and Highway Navigation Safety",
                "summary": "Rules for renting cars, motorbikes (e.g. Royal Enfield Ladakh trips), and understanding Indian road dynamics.",
                "warning_signs": "Poorly maintained rental brakes or bald tires; sudden cattle crossings; unbanked hairpin bends in mountain ghats.",
                "dos": "Wear a certified helmet and protective gear at all times on two-wheelers; carry an International Driving Permit (IDP) and national license; use GPS navigation with offline maps.",
                "donts": "Do not drive under the influence of alcohol (zero tolerance limit); avoid aggressive overtaking on narrow single-lane ghat roads.",
                "emergency_guidance": "Highway Police Helpline: 1033 (National Highways Authority of India) or 112.",
                "icon_name": "compass"
            },
            {
                "category": "Cybersecurity and Travel Scams",
                "title": "Digital Safety, Public Wi-Fi & Tourist Scam Defense",
                "summary": "Guarding against SIM swap fraud, ATM skimming, fake booking sites, and prevalent tourist tout scams.",
                "warning_signs": "Offers to purchase gemstones or antiques with promises of resale abroad; unsolicited calls asking for OTPs or credit card CVV.",
                "dos": "Use a secure VPN on public airport/hotel Wi-Fi networks; inspect ATM card slots for skimmers before inserting cards; buy SIM cards only from official telecom brand stores.",
                "donts": "Never scan unknown QR codes that promise to 'send' you money; do not hand over your original passport to hotel clerks overnight for prolonged scanning.",
                "emergency_guidance": "Report cyber financial fraud immediately at National Cyber Crime Portal (1930) and freeze compromised bank cards.",
                "icon_name": "lock"
            },
            {
                "category": "Natural Disaster Preparedness",
                "title": "Monsoon Floods, Cyclones & Earthquake Response",
                "summary": "Contingency preparedness for flash floods, landslides, coastal cyclones, and seismic activity.",
                "warning_signs": "IMD (India Meteorological Department) Red or Orange weather alerts; sudden murky discoloration of mountain streams.",
                "dos": "Follow NDMA (National Disaster Management Authority) bulletins; keep an emergency power bank charged; stay indoors during cyclone landfalls.",
                "donts": "Do not drive through submerged causeways; never build tents directly on dry riverbeds in monsoon season.",
                "emergency_guidance": "NDMA Disaster Helpline: 1078 or state emergency 1070 or 112.",
                "icon_name": "cloud-rain"
            },
            {
                "category": "Medical Emergency Procedures",
                "title": "Heat Stroke, Waterborne Illness & First Aid",
                "summary": "Handling tropical dehydration, food hygiene adjustments, dog bites (rabies prophylaxis), and finding certified clinics.",
                "warning_signs": "Extreme fatigue and cessation of sweating (heat stroke); high fever and severe stomach cramps; animal bite or scratch.",
                "dos": "Drink oral rehydration salts (ORS) in hot climates; wash hands frequently; seek immediate post-exposure rabies vaccination if bitten by any street animal.",
                "donts": "Never drink untreated tap water; avoid eating precut salads or raw peeled fruits from roadside open stalls.",
                "emergency_guidance": "Call Ambulance 102 or 108 or National Emergency 112 immediately. Geonova provides direct hospital navigation.",
                "icon_name": "activity"
            },
            {
                "category": "Lost Passport or Travel Document Procedures",
                "title": "Steps for Lost Passport, Visa or Driving License",
                "summary": "Clear, step-by-step statutory protocol for foreign and domestic tourists facing document loss.",
                "warning_signs": "Unzipped bag compartments in crowded bazaars or unattended luggage at railway cloakrooms.",
                "dos": "Store digital copies in your Geonova Document Vault; file a digital or physical Police Lost Report (e-FIR) immediately; contact your home embassy or consulate.",
                "donts": "Do not attempt to travel domestically by commercial flight without an official police FIR or emergency travel certificate.",
                "emergency_guidance": "Visit the nearest tourist police station to get a stamped Lost Document Certificate, then contact FRRO (Foreigners Regional Registration Office) at https://indianfrro.gov.in.",
                "icon_name": "file-text"
            }
        ]

        for p in protocols_data:
            db.add(models.SafetyProtocol(**p))

        # 6. Seed Curated Tourism Packages
        packages_data = [
            {
                "state_id": dl_state.id,
                "title": "Golden Triangle Royal Heritage Circuit",
                "destination": "Delhi, Agra & Jaipur",
                "duration_days": 6,
                "duration_nights": 5,
                "price": 24999.0,
                "discount_price": 19999.0,
                "travel_type": "Heritage & Culture",
                "max_group_size": 12,
                "accommodation": "4-Star Heritage Palaces & Hotels",
                "transportation": "Private AC Luxury Innova with Chauffeur",
                "meals": "Buffet Breakfast & Traditional Dinners Included",
                "guide_included": True,
                "safety_features": "GPS Monitored Vehicle, Certified Multi-Lingual Guide, First Aid Kit",
                "itinerary": "Day 1: Old & New Delhi Heritage Tour (Qutub Minar, India Gate, Chandni Chowk). Day 2: Drive to Agra, sunset visit to Mehtab Bagh. Day 3: Sunrise at Taj Mahal, Agra Fort, drive to Fatehpur Sikri. Day 4: Arrive in Jaipur, explore Amber Fort and Jal Mahal. Day 5: City Palace, Jantar Mantar, and local bazaar walk. Day 6: Return to Delhi with airport handoff.",
                "image_url": "https://images.unsplash.com/photo-1564507592333-c60657eea523?auto=format&fit=crop&w=600&q=80",
                "rating": 4.9,
                "reviews_count": 128
            },
            {
                "state_id": kl_state.id,
                "title": "Kerala Backwaters & Mist Tea Serenity",
                "destination": "Kochi, Munnar & Alleppey",
                "duration_days": 5,
                "duration_nights": 4,
                "price": 21500.0,
                "discount_price": 17999.0,
                "travel_type": "Family & Nature",
                "max_group_size": 10,
                "accommodation": "Eco Resort in Munnar + AC Deluxe Houseboat",
                "transportation": "AC Private Sedan with English-speaking driver",
                "meals": "All Meals on Houseboat + Daily Breakfast",
                "guide_included": True,
                "safety_features": "Drishti Certified Lifeguards, Onboard Lifejackets, 24/7 Concierge",
                "itinerary": "Day 1: Fort Kochi colonial walk and Chinese fishing nets. Day 2: Scenic drive to Munnar, Cheeyappara waterfalls, tea museum. Day 3: Eravikulam National Park and Mattupetty Dam. Day 4: Board traditional houseboat in Alleppey, leisurely backwaters cruise through tranquil villages. Day 5: Traditional Kerala breakfast and departure transfer to Kochi airport.",
                "image_url": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=600&q=80",
                "rating": 4.95,
                "reviews_count": 94
            },
            {
                "state_id": ga_state.id,
                "title": "Goa Coastal Sun, Spice & Heritage Haven",
                "destination": "Panaji, Old Goa & South Goa Coast",
                "duration_days": 4,
                "duration_nights": 3,
                "price": 15999.0,
                "discount_price": 13499.0,
                "travel_type": "Leisure & Coastal",
                "max_group_size": 15,
                "accommodation": "Beachside 4-Star Boutique Resort",
                "transportation": "AC Coach for Sightseeing + Airport Transfers",
                "meals": "Daily Gourmet Breakfast & Seafood Welcome Dinner",
                "guide_included": True,
                "safety_features": "Water Safety Certified, Licensed Island Cruise, Women Guide Option",
                "itinerary": "Day 1: Welcome to Goa, sunset beach walk and Portuguese dinner. Day 2: Old Goa UNESCO Cathedrals, Latin Quarter walking tour, and Mandovi River sunset cruise. Day 3: Sahakari Spice Farm excursion with traditional buffet lunch and leisurely afternoon at Palolem Beach. Day 4: Morning dolphin watch cruise and airport transfer.",
                "image_url": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=600&q=80",
                "rating": 4.88,
                "reviews_count": 142
            }
        ]

        for pkg in packages_data:
            db.add(models.TourismPackage(**pkg))

        # 7. Seed Sample User Document
        doc1 = models.Document(
            user_id=tourist_user.id,
            document_type="Passport",
            document_name="Indian Passport (Aarav Mehta)",
            document_number="Z4892110",
            expiry_date="2031-10-15",
            file_type="pdf",
            file_size_kb=240,
            status="valid"
        )
        doc2 = models.Document(
            user_id=tourist_user.id,
            document_type="Travel Insurance",
            document_name="National Travel Shield Policy",
            document_number="POL-2026-9811",
            expiry_date="2026-10-01",
            file_type="pdf",
            file_size_kb=180,
            status="expiring_soon"
        )
        db.add_all([doc1, doc2])

        db.commit()
        print("Database seeded successfully with all 36 States & UTs, authorities, protocols, geofences and users!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
