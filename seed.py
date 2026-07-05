from app.core.database import SessionLocal
from app.models.models import Topic, Vocabulary, Essay

db = SessionLocal()

# ─── TOPICS ───────────────────────────────────
topics = [
    Topic(name_en="Technology", name_uz="Texnologiya", icon="💻"),
    Topic(name_en="Education", name_uz="Ta'lim", icon="📚"),
    Topic(name_en="Environment", name_uz="Atrof-muhit", icon="🌍"),
    Topic(name_en="Health", name_uz="Sog'liq", icon="🏥"),
    Topic(name_en="Society", name_uz="Jamiyat", icon="👥"),
    Topic(name_en="Transport", name_uz="Transport", icon="🚗"),
    Topic(name_en="Media", name_uz="Media", icon="📱"),
    Topic(name_en="Economy", name_uz="Iqtisodiyot", icon="💰"),
    Topic(name_en="Crime", name_uz="Jinoyat", icon="⚖️"),
    Topic(name_en="Culture", name_uz="Madaniyat", icon="🎭"),
]

for topic in topics:
    existing = db.query(Topic).filter(
        Topic.name_en == topic.name_en
    ).first()
    if not existing:
        db.add(topic)

db.commit()
print("✅ Topics qo'shildi!")

# ─── VOCABULARY ───────────────────────────────
tech_topic = db.query(Topic).filter(
    Topic.name_en == "Technology"
).first()

edu_topic = db.query(Topic).filter(
    Topic.name_en == "Education"
).first()

env_topic = db.query(Topic).filter(
    Topic.name_en == "Environment"
).first()

vocabulary = [
    # Technology
    Vocabulary(
        word="instantaneous",
        translation_uz="bir zumda bo'ladigan, darhol",
        word_type="Adj",
        cefr_level="C1",
        topic_id=tech_topic.id,
        definition_uz="Juda tez sodir bo'ladigan, deyarli vaqt ketmaydigan",
        example_1="Email allows instantaneous communication across the globe.",
        example_2="The instantaneous response of the system impressed everyone.",
        example_3="Modern technology enables instantaneous data transfer.",
    ),
    Vocabulary(
        word="facilitate",
        translation_uz="osonlashtirmoq, imkon yaratmoq",
        word_type="Verb",
        cefr_level="C1",
        topic_id=tech_topic.id,
        definition_uz="Biror jarayonni osonroq yoki tezroq qilmoq",
        example_1="Technology facilitates communication between people.",
        example_2="Online platforms facilitate remote learning effectively.",
        example_3="AI tools facilitate data analysis significantly.",
        collocations=["facilitate learning", "facilitate communication", "facilitate access"],
        synonyms=["enable", "assist", "support"],
    ),
    Vocabulary(
        word="unprecedented",
        translation_uz="misli ko'rilmagan, tarixda bo'lmagan",
        word_type="Adj",
        cefr_level="C2",
        topic_id=tech_topic.id,
        definition_uz="Avval hech qachon bo'lmagan darajada katta yoki muhim",
        example_1="The internet caused unprecedented changes in communication.",
        example_2="AI development is proceeding at an unprecedented pace.",
        example_3="The pandemic created unprecedented challenges worldwide.",
    ),
    Vocabulary(
        word="disseminate",
        translation_uz="keng tarqatmoq, ko'plab odamlarga yetkazmoq",
        word_type="Verb",
        cefr_level="C2",
        topic_id=tech_topic.id,
        definition_uz="Ma'lumot yoki g'oyani keng auditoriyaga tarqatmoq",
        example_1="Social media disseminates information rapidly.",
        example_2="The government disseminated health guidelines widely.",
        example_3="Universities disseminate knowledge through research.",
    ),
    Vocabulary(
        word="streamline",
        translation_uz="soddalashtirmoq, samaraliroq qilmoq",
        word_type="Verb",
        cefr_level="C1",
        topic_id=tech_topic.id,
        definition_uz="Jarayonni tezroq va samaraliroq qilish",
        example_1="Technology streamlines business operations significantly.",
        example_2="The new software streamlines data management.",
        example_3="Automation streamlines repetitive tasks efficiently.",
    ),
    # Education
    Vocabulary(
        word="pedagogical",
        translation_uz="pedagogik, ta'limga oid",
        word_type="Adj",
        cefr_level="C2",
        topic_id=edu_topic.id,
        definition_uz="O'qitish va ta'lim metodlariga oid",
        example_1="Teachers must develop strong pedagogical skills.",
        example_2="The pedagogical approach varies across cultures.",
        example_3="New pedagogical methods improve student engagement.",
    ),
    Vocabulary(
        word="critical thinking",
        translation_uz="tanqidiy fikrlash",
        word_type="Phrase",
        cefr_level="B2",
        topic_id=edu_topic.id,
        definition_uz="Ma'lumotni chuqur tahlil qilib, to'g'ri xulosa chiqarish qobiliyati",
        example_1="Education should develop critical thinking skills.",
        example_2="Critical thinking helps solve complex problems.",
        example_3="Universities encourage critical thinking among students.",
    ),
    Vocabulary(
        word="personalised learning",
        translation_uz="shaxslashtirilgan ta'lim",
        word_type="Phrase",
        cefr_level="C1",
        topic_id=edu_topic.id,
        definition_uz="Har bir o'quvchining ehtiyojiga mos ta'lim usuli",
        example_1="AI enables personalised learning for every student.",
        example_2="Personalised learning improves educational outcomes.",
        example_3="Online platforms offer personalised learning paths.",
    ),
    # Environment
    Vocabulary(
        word="sustainable",
        translation_uz="barqaror, uzoq muddatli, ekologik",
        word_type="Adj",
        cefr_level="B2",
        topic_id=env_topic.id,
        definition_uz="Tabiatga zarar yetkazmay uzoq vaqt davom ettirish mumkin bo'lgan",
        example_1="We need sustainable energy sources for the future.",
        example_2="Sustainable farming protects the environment.",
        example_3="Cities must develop sustainable transport systems.",
        collocations=["sustainable development", "sustainable energy", "sustainable future"],
    ),
    Vocabulary(
        word="carbon footprint",
        translation_uz="karbon izi — CO2 chiqarish miqdori",
        word_type="Phrase",
        cefr_level="C1",
        topic_id=env_topic.id,
        definition_uz="Bir shaxs yoki tashkilotning atmosferaga chiqaradigan CO2 miqdori",
        example_1="Flying increases your carbon footprint significantly.",
        example_2="Companies must reduce their carbon footprint.",
        example_3="Electric cars have a smaller carbon footprint.",
    ),
    Vocabulary(
        word="biodiversity",
        translation_uz="biologik xilma-xillik",
        word_type="Noun",
        cefr_level="C1",
        topic_id=env_topic.id,
        definition_uz="Yerda mavjud bo'lgan turli o'simlik va hayvonlar xilma-xilligi",
        example_1="Deforestation threatens biodiversity worldwide.",
        example_2="Protecting biodiversity is essential for ecosystems.",
        example_3="Climate change reduces global biodiversity rapidly.",
    ),
]

for vocab in vocabulary:
    existing = db.query(Vocabulary).filter(
        Vocabulary.word == vocab.word
    ).first()
    if not existing:
        db.add(vocab)

db.commit()
print("✅ Vocabulary qo'shildi!")

# ─── ESSAYS ───────────────────────────────────
tech_topic = db.query(Topic).filter(
    Topic.name_en == "Technology"
).first()

essays = [
    Essay(
        title="The Impact of Technology on Communication",
        topic_id=tech_topic.id,
        question_type="evaluation",
        band_score=8.0,
        content="""In today's hyper-connected world, technology has fundamentally transformed the way people communicate. While some argue that digital communication has made human interaction more instantaneous and convenient, others contend that it has rendered relationships increasingly impersonal. This essay will evaluate both perspectives before reaching a reasoned conclusion.

The most compelling advantage of technology-driven communication is its unprecedented speed and accessibility. Email, for instance, facilitates cross-border communication at virtually no cost, allowing individuals and businesses to disseminate information to thousands of recipients within seconds. This has streamlined global commerce and made international collaboration seamless. Furthermore, social media platforms have given a voice to the previously voiceless, enabling ordinary citizens to raise awareness about critical issues on a global scale.

However, the drawbacks of digital communication are equally significant. Face-to-face interaction provides non-verbal cues such as tone of voice, facial expressions and body language that convey meaning far more effectively than text. The absence of these cues in digital messages frequently leads to misinterpretation and miscommunication. Moreover, the constant bombardment of notifications causes information overload and inbox fatigue, ultimately reducing rather than enhancing productivity.

In conclusion, while technology has created unprecedented opportunities for connection and collaboration, it cannot fully replicate the depth of human interaction. A balanced approach — embracing digital tools while preserving meaningful face-to-face communication — appears to be the most prudent course of action.""",
        word_count=214,
    ),
    Essay(
        title="Should Governments Invest More in Education?",
        topic_id=edu_topic.id,
        question_type="reasoning",
        band_score=7.5,
        content="""Education is widely regarded as the cornerstone of societal progress, yet governments worldwide continue to debate how much public funding it deserves. This essay argues that increased government investment in education is not merely desirable but absolutely essential for long-term national development.

First and foremost, a well-educated population drives economic growth. When citizens possess strong critical thinking skills and technical expertise, they become more productive members of the workforce, capable of innovating and adapting to an ever-changing economy. Countries that have prioritised educational investment, such as Finland and South Korea, consistently outperform their peers in both academic achievement and economic competitiveness. This evidence suggests a direct correlation between educational expenditure and national prosperity.

Furthermore, education serves as the most powerful tool for reducing social inequality. Children from disadvantaged backgrounds who receive quality education are significantly more likely to break the cycle of poverty. Without adequate government funding, personalised learning opportunities remain accessible only to those who can afford private schooling, thereby exacerbating existing inequalities and undermining social cohesion.

In conclusion, the long-term benefits of investing in education — economic growth, social mobility and reduced inequality — far outweigh the short-term financial costs. Governments that neglect this responsibility do so at the peril of their nation's future.""",
        word_count=198,
    ),
]

for essay in essays:
    existing = db.query(Essay).filter(
        Essay.title == essay.title
    ).first()
    if not existing:
        db.add(essay)

db.commit()
print("✅ Essays qo'shildi!")

db.close()
print("\n🎉 Seed data muvaffaqiyatli qo'shildi!")
print(f"📚 Topics: {len(topics)}")
print(f"🧠 Vocabulary: {len(vocabulary)}")
print(f"✍️  Essays: {len(essays)}")