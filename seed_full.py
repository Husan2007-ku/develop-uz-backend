from app.core.database import SessionLocal
from app.models.models import Topic, Vocabulary, Essay, GrammarStructure, SpeakingQuestion, SpeakingAnswer

db = SessionLocal()

# ─── TOPICS ───────────────────────────────────────────────
topics_data = [
    ("Technology", "Texnologiya", "💻"),
    ("Education", "Ta'lim", "📚"),
    ("Environment", "Atrof-muhit", "🌍"),
    ("Health", "Sog'liq", "🏥"),
    ("Society", "Jamiyat", "👥"),
    ("Transport", "Transport", "🚗"),
    ("Media", "Media", "📱"),
    ("Economy", "Iqtisodiyot", "💰"),
    ("Crime", "Jinoyat", "⚖️"),
    ("Culture", "Madaniyat", "🎭"),
]

topics = {}
for name_en, name_uz, icon in topics_data:
    existing = db.query(Topic).filter(Topic.name_en == name_en).first()
    if not existing:
        t = Topic(name_en=name_en, name_uz=name_uz, icon=icon)
        db.add(t)
        db.flush()
        topics[name_en] = t
    else:
        topics[name_en] = existing

db.commit()
print(f"✅ Topics: {len(topics)}")

# ─── VOCABULARY ───────────────────────────────────────────
vocab_data = [
    # Technology — C1
    ("exacerbate", "yomonlashtirmoq, kuchaytirmoq", "Verb", "C1", "Technology",
     "yomonlashadi degani", "Climate change will exacerbate water shortages.",
     "Social media exacerbates feelings of anxiety.", "Technology exacerbates inequality.",
     ["exacerbate a problem", "exacerbate tensions", "exacerbate inequality"],
     ["worsen", "aggravate", "intensify"],
     {"noun": "exacerbation", "adj": "exacerbated"}),

    ("facilitate", "osonlashtirmoq, imkon yaratmoq", "Verb", "C1", "Technology",
     "jarayonni yengillashtirish", "Technology facilitates communication.",
     "Online platforms facilitate remote learning.", "AI tools facilitate data analysis.",
     ["facilitate learning", "facilitate communication", "facilitate access"],
     ["enable", "assist", "support"], {"noun": "facilitation", "adj": "facilitated"}),

    ("unprecedented", "misli ko'rilmagan", "Adj", "C2", "Technology",
     "tarixda bo'lmagan darajada", "The internet caused unprecedented changes.",
     "AI development is proceeding at an unprecedented pace.",
     "The pandemic created unprecedented challenges.",
     ["unprecedented scale", "unprecedented growth", "unprecedented speed"],
     ["unparalleled", "unmatched", "extraordinary"], {}),

    ("disseminate", "keng tarqatmoq", "Verb", "C2", "Technology",
     "ma'lumotni ko'pchilikka yetkazish", "Social media disseminates information rapidly.",
     "Governments disseminate health guidelines.", "Universities disseminate knowledge.",
     ["disseminate information", "disseminate knowledge", "disseminate ideas"],
     ["spread", "distribute", "circulate"], {"noun": "dissemination"}),

    ("streamline", "soddalashtirmoq, samaraliroq qilmoq", "Verb", "C1", "Technology",
     "jarayonni tezroq va samaraliroq qilish", "Technology streamlines business operations.",
     "The new software streamlines data management.", "Automation streamlines tasks.",
     ["streamline operations", "streamline processes", "streamline workflow"],
     ["simplify", "optimise", "improve"], {"noun": "streamlining"}),

    ("instantaneous", "bir zumda bo'ladigan", "Adj", "C1", "Technology",
     "darhol sodir bo'ladigan", "Email allows instantaneous communication.",
     "The response was instantaneous.", "Modern tech enables instantaneous data transfer.",
     ["instantaneous communication", "instantaneous response", "instantaneous access"],
     ["immediate", "instant", "simultaneous"], {"adv": "instantaneously"}),

    ("ubiquitous", "hamma joyda mavjud", "Adj", "C2", "Technology",
     "hamma yerda uchrash", "Smartphones have become ubiquitous.",
     "Social media is now ubiquitous in daily life.",
     "AI is becoming ubiquitous across industries.",
     ["ubiquitous technology", "ubiquitous presence", "ubiquitous access"],
     ["widespread", "pervasive", "omnipresent"], {"adv": "ubiquitously"}),

    # Education — C1/C2
    ("pedagogical", "pedagogik", "Adj", "C2", "Education",
     "o'qitish metodlariga oid", "Teachers must develop pedagogical skills.",
     "The pedagogical approach varies across cultures.",
     "New pedagogical methods improve engagement.",
     ["pedagogical approach", "pedagogical methods", "pedagogical skills"],
     ["educational", "instructional"], {"noun": "pedagogy"}),

    ("curriculum", "o'quv dasturi", "Noun", "C1", "Education",
     "maktab yoki universitetning o'quv rejasi",
     "The curriculum should include critical thinking.",
     "Schools are reforming their curriculum.",
     "A well-designed curriculum prepares students for the future.",
     ["design a curriculum", "revise the curriculum", "follow the curriculum"],
     ["syllabus", "programme", "course"], {}),

    ("foster", "rivojlantirmoq, tarbiyalamoq", "Verb", "C1", "Education",
     "o'stirish, qo'llab-quvvatlash",
     "Education should foster creativity.", "Schools must foster critical thinking.",
     "Parents play a key role in fostering curiosity.",
     ["foster creativity", "foster learning", "foster development"],
     ["encourage", "nurture", "cultivate"], {"noun": "fostering"}),

    ("rote learning", "yodlab o'rganish", "Phrase", "C1", "Education",
     "tushunmasdan yodlab olish",
     "Rote learning stifles creativity.",
     "Many Asian schools rely on rote learning.",
     "Educators criticise rote learning as ineffective.",
     ["rely on rote learning", "rote learning approach", "beyond rote learning"],
     ["memorisation", "mechanical learning"], {}),

    ("holistic", "yaxlit, to'liq", "Adj", "C1", "Education",
     "barcha tomonlarni qamrab oluvchi",
     "Education should take a holistic approach.",
     "Holistic development includes emotional and social skills.",
     "A holistic curriculum prepares well-rounded graduates.",
     ["holistic approach", "holistic development", "holistic education"],
     ["comprehensive", "all-encompassing", "integrated"], {"adv": "holistically"}),

    # Environment — C1/C2
    ("sustainable", "barqaror, ekologik", "Adj", "B2", "Environment",
     "tabiatga zarar yetkazmay davom ettirish mumkin",
     "We need sustainable energy sources.", "Sustainable farming protects nature.",
     "Cities must develop sustainable transport.",
     ["sustainable development", "sustainable energy", "sustainable future"],
     ["eco-friendly", "renewable", "green"], {"adv": "sustainably", "noun": "sustainability"}),

    ("carbon footprint", "karbon izi", "Phrase", "C1", "Environment",
     "CO2 chiqarish miqdori",
     "Flying increases your carbon footprint.", "Companies must reduce their carbon footprint.",
     "Electric cars have a smaller carbon footprint.",
     ["reduce carbon footprint", "calculate carbon footprint", "carbon footprint offset"],
     ["emissions", "environmental impact"], {}),

    ("biodiversity", "biologik xilma-xillik", "Noun", "C1", "Environment",
     "turli o'simlik va hayvonlar xilma-xilligi",
     "Deforestation threatens biodiversity.", "Protecting biodiversity is essential.",
     "Climate change reduces global biodiversity.",
     ["protect biodiversity", "loss of biodiversity", "preserve biodiversity"],
     ["ecological diversity", "species diversity"], {}),

    ("mitigation", "yumshatish, kamaytirish", "Noun", "C2", "Environment",
     "zararni kamaytirish choralari",
     "Governments focus on climate change mitigation.",
     "Mitigation strategies include renewable energy adoption.",
     "Mitigation alone is insufficient without adaptation.",
     ["climate mitigation", "risk mitigation", "mitigation strategies"],
     ["reduction", "alleviation", "minimisation"], {"verb": "mitigate"}),

    # Society — C1/C2
    ("inequality", "tengsizlik", "Noun", "B2", "Society",
     "imkoniyat yoki boylik taqsimotidagi nomutanosiblik",
     "Income inequality is widening globally.", "Education inequality affects opportunities.",
     "Gender inequality persists in many societies.",
     ["income inequality", "social inequality", "address inequality"],
     ["disparity", "imbalance", "gap"], {"adj": "unequal"}),

    ("marginalised", "chetlashtirilgan", "Adj", "C2", "Society",
     "jamiyatdan chetlashtirilgan guruhlar",
     "Marginalised communities lack access to education.",
     "Governments must support marginalised groups.",
     "Social policies should address marginalised populations.",
     ["marginalised communities", "marginalised groups", "marginalised individuals"],
     ["disadvantaged", "excluded", "vulnerable"], {"verb": "marginalise"}),

    ("cohesion", "birlik, hamjihatlik", "Noun", "C2", "Society",
     "jamiyat a'zolari o'rtasidagi birlik",
     "Immigration can challenge social cohesion.",
     "Strong communities are built on social cohesion.",
     "Economic inequality undermines social cohesion.",
     ["social cohesion", "community cohesion", "national cohesion"],
     ["unity", "solidarity", "harmony"], {"adj": "cohesive"}),

    # Health — C1/C2
    ("prevalent", "keng tarqalgan", "Adj", "C1", "Health",
     "ko'p uchraydigan, keng tarqalgan",
     "Obesity is increasingly prevalent in developed nations.",
     "Mental health issues are prevalent among young people.",
     "Diabetes is prevalent in sedentary populations.",
     ["increasingly prevalent", "highly prevalent", "prevalent condition"],
     ["widespread", "common", "pervasive"], {"noun": "prevalence", "adv": "prevalently"}),

    ("sedentary", "harakatsiz", "Adj", "C1", "Health",
     "o'tirib qoladigan, jismoniy faoliyatsiz",
     "A sedentary lifestyle increases health risks.",
     "Modern technology promotes sedentary behaviour.",
     "Sedentary jobs contribute to obesity.",
     ["sedentary lifestyle", "sedentary behaviour", "sedentary work"],
     ["inactive", "stationary"], {"noun": "sedentariness"}),

    # Media — C1/C2
    ("proliferation", "ko'payish, tarqalish", "Noun", "C2", "Media",
     "tez sur'atda ko'payish yoki tarqalish",
     "The proliferation of social media has transformed communication.",
     "Nuclear proliferation remains a global threat.",
     "The proliferation of fake news undermines democracy.",
     ["proliferation of", "nuclear proliferation", "rapid proliferation"],
     ["spread", "expansion", "multiplication"], {"verb": "proliferate"}),

    ("algorithm", "algoritm", "Noun", "C1", "Media",
     "ma'lumotlarni qayta ishlovchi dastur qoidalar to'plami",
     "Social media algorithms shape what users see.",
     "Algorithms can reinforce existing biases.",
     "Tech companies rely on algorithms to personalise content.",
     ["social media algorithm", "algorithm bias", "recommendation algorithm"],
     ["formula", "system", "programme"], {}),

    # Economy — C1/C2
    ("exacerbate", "yomonlashtirmoq", "Verb", "C1", "Economy",
     "muammoni yanada og'irlashtirish",
     "The recession exacerbated unemployment rates.",
     "Trade wars exacerbate economic uncertainty.",
     "Inflation exacerbates poverty in developing nations.",
     ["exacerbate poverty", "exacerbate unemployment", "exacerbate inequality"],
     ["worsen", "aggravate", "intensify"], {"noun": "exacerbation"}),

    ("disposable income", "erkin daromad", "Phrase", "C1", "Economy",
     "soliqdan keyin qoladigan sarflash uchun pul",
     "Rising disposable income boosts consumer spending.",
     "Families with low disposable income struggle to save.",
     "Tax cuts increase household disposable income.",
     ["disposable income levels", "low disposable income", "increase disposable income"],
     ["net income", "take-home pay"], {}),
]

added_vocab = 0
for item in vocab_data:
    word, translation_uz, word_type, cefr_level, topic_name, definition_uz, ex1, ex2, ex3, collocations, synonyms, word_family = item
    existing = db.query(Vocabulary).filter(Vocabulary.word == word, Vocabulary.topic_id == topics[topic_name].id).first()
    if not existing:
        v = Vocabulary(
            word=word, translation_uz=translation_uz, word_type=word_type,
            cefr_level=cefr_level, topic_id=topics[topic_name].id,
            definition_uz=definition_uz, example_1=ex1, example_2=ex2, example_3=ex3,
            collocations=collocations, synonyms=synonyms, word_family=word_family
        )
        db.add(v)
        added_vocab += 1

db.commit()
print(f"✅ Vocabulary: {added_vocab} ta yangi qo'shildi")

# ─── ESSAYS ───────────────────────────────────────────────
essays_data = [
    ("The Impact of Social Media on Mental Health", "Society", "evaluation", 8.0, """In the contemporary digital landscape, social media platforms have become an inescapable feature of daily life, particularly among younger generations. While proponents argue that these platforms foster unprecedented levels of connectivity and community, a compelling body of evidence suggests that excessive social media use may significantly exacerbate mental health issues, including anxiety, depression, and diminished self-esteem.

The most persuasive argument against unrestricted social media use concerns the phenomenon of social comparison. Platforms such as Instagram and TikTok are inherently designed to showcase curated, idealised versions of users' lives. When individuals — particularly adolescents, whose identities are still forming — consistently measure themselves against these carefully constructed highlight reels, the psychological consequences can be devastating. Research published in the Journal of Social and Clinical Psychology demonstrates a direct correlation between passive social media consumption and elevated rates of depression and loneliness.

Furthermore, the addictive architecture of social media platforms poses serious risks to cognitive development and productivity. Algorithms specifically engineered to maximise engagement exploit psychological vulnerabilities, trapping users in cycles of compulsive scrolling. This inevitably leads to sleep deprivation, reduced concentration spans, and a diminished capacity for deep, focused work — consequences that are particularly alarming among school-age children.

Admittedly, social media is not without merit. It has given a voice to the voiceless, enabled grassroots social movements, and provided vital communities for individuals who might otherwise feel isolated. During the COVID-19 pandemic, for instance, platforms such as Zoom and Instagram played an indispensable role in maintaining social bonds.

In conclusion, while social media undeniably offers certain social benefits, the weight of evidence suggests that its negative psychological impact outweighs its advantages, particularly for vulnerable demographics. Governments and technology companies must collaborate to implement robust safeguards, including algorithm transparency and screen time regulations, to mitigate these harms.""", 214),

    ("Should University Education Be Free?", "Education", "reasoning", 7.5, """The question of whether university education should be provided free of charge to all students has generated intense debate across the political spectrum. While advocates of free higher education cite principles of equality and social mobility, opponents contend that such a policy is fiscally unsustainable and may paradoxically undermine educational quality.

The most compelling argument in favour of free university education is its potential to dismantle entrenched socioeconomic barriers. In systems where tuition fees are prohibitively high, higher education effectively becomes a privilege of the wealthy rather than a right accessible to all. First-generation students from low-income backgrounds are disproportionately deterred by the prospect of substantial debt, perpetuating cycles of poverty and inequality. Countries such as Germany and Norway, which provide tuition-free higher education, consistently produce highly educated, globally competitive workforces — evidence that the model is both viable and effective.

However, the financial implications of eliminating tuition fees cannot be dismissed. Universities require substantial funding to maintain world-class faculty, state-of-the-art research facilities, and comprehensive student services. If government funding fails to adequately compensate for lost tuition revenue, institutional quality may deteriorate, ultimately harming the very students the policy seeks to benefit. Moreover, critics argue that free university education disproportionately subsidises middle-class students who would have attended university regardless, rather than targeting resources at those most in need.

A more pragmatic solution might involve income-contingent loan schemes, wherein graduates repay their education costs only upon reaching a comfortable income threshold. This approach balances accessibility with fiscal responsibility, ensuring that universities remain adequately funded while preventing debt from deterring talented students.

In conclusion, while the aspiration for universal access to higher education is admirable, a blanket free tuition policy may prove financially and practically unworkable. A targeted, income-contingent funding model represents a more equitable and sustainable alternative.""", 253),

    ("Technology and Privacy: Are We Sacrificing Too Much?", "Technology", "evaluation", 8.5, """The relentless advance of digital technology has ushered in an era of unprecedented convenience, connectivity, and innovation. Yet this progress has come at a profound cost: the systematic erosion of individual privacy. As governments and corporations accumulate vast quantities of personal data, a fundamental question demands urgent attention — are the benefits of technological advancement worth the sacrifice of our most intimate freedoms?

The scale of contemporary data collection is staggering. Tech giants such as Google, Meta, and Amazon harvest detailed information about users' behaviours, preferences, locations, and social networks, often without meaningful informed consent. This data is subsequently monetised through targeted advertising — a business model that treats human attention and personal information as commodities. More troubling still, the Cambridge Analytica scandal demonstrated that such data can be weaponised to manipulate democratic processes, raising existential concerns about the integrity of electoral systems.

Governments, too, have not resisted the temptation to exploit surveillance technologies. Mass surveillance programmes, justified in the name of national security, have been revealed to monitor citizens on an industrial scale. What is particularly alarming is that such systems disproportionately target marginalised communities, reinforcing existing inequalities rather than protecting all citizens equally.

Proponents of data collection argue that personalised services, improved healthcare outcomes through data analytics, and enhanced security capabilities represent genuine public benefits. These arguments are not without merit. However, the fundamental asymmetry of power between data-collecting institutions and individual citizens renders truly voluntary consent virtually impossible.

In conclusion, while technology has undeniably enriched human life in countless ways, the current paradigm of unchecked data extraction represents an unacceptable infringement on fundamental rights. Robust regulatory frameworks — such as the European Union's General Data Protection Regulation — must be strengthened and universalised to ensure that technological progress does not come at the expense of human dignity.""", 271),

    ("The Advantages and Disadvantages of Globalisation", "Economy", "comparison", 7.0, """Globalisation — the process by which economies, societies, and cultures have become increasingly interconnected — represents one of the most transformative forces of the modern era. While it has generated remarkable economic growth and cultural exchange, its critics contend that its benefits are distributed profoundly unevenly, exacerbating inequality both within and between nations.

The economic case for globalisation is substantial. Free trade agreements have enabled developing nations to access global markets, attract foreign investment, and achieve rapid industrialisation. Countries such as South Korea, China, and Vietnam have lifted hundreds of millions of people out of poverty within a single generation — a development that would have been inconceivable without integration into the global economy. Furthermore, consumers worldwide benefit from lower prices and greater product variety, directly improving living standards.

Nevertheless, the distributional consequences of globalisation are deeply troubling. While overall wealth has increased, the gains have been disproportionately captured by multinational corporations and their shareholders, while workers in developed nations have seen their wages stagnate as manufacturing jobs migrate to lower-cost economies. The resulting economic anxiety has fuelled political polarisation and the rise of nationalist movements across Europe and North America.

Moreover, globalisation has enabled the transnational spread of environmental degradation. As corporations relocate production to countries with weaker regulatory frameworks, pollution and resource depletion follow. The global supply chains that deliver cheap consumer goods frequently rely on exploitative labour practices and generate enormous carbon emissions.

In conclusion, globalisation is neither inherently beneficial nor inherently harmful — its consequences depend entirely on the governance frameworks that shape it. With appropriate international regulation, fairer trade agreements, and robust social safety nets, globalisation's considerable potential can be harnessed while mitigating its most damaging effects.""", 261),

    ("The Role of Government in Addressing Climate Change", "Environment", "reasoning", 8.0, """Climate change represents arguably the most pressing existential challenge confronting humanity. While individual behavioural change and corporate responsibility undoubtedly play important roles, the scale and urgency of the crisis are such that only decisive government intervention can deliver the systemic transformation required to avert catastrophe.

Governments possess unique tools that no other actor can deploy at comparable scale or speed. Regulatory frameworks can mandate emissions reductions across entire industries, eliminating the competitive disadvantages that deter individual companies from acting unilaterally. Carbon pricing mechanisms — whether through direct taxes or cap-and-trade systems — create economy-wide incentives to decarbonise, channelling market forces towards sustainable outcomes. The European Union's Emissions Trading System provides compelling evidence that well-designed regulatory frameworks can deliver meaningful emissions reductions without sacrificing economic growth.

Furthermore, governments are uniquely positioned to mobilise the investment required for the energy transition. The development of renewable energy infrastructure, smart grids, and green hydrogen technology demands capital expenditure on a scale that private markets alone cannot reliably deliver, particularly in developing economies. Public investment in research and development has historically underpinned virtually every major technological breakthrough, from the internet to mRNA vaccines, and clean energy is no exception.

Critics argue that government intervention distorts markets and risks picking technological winners prematurely. While these concerns deserve serious consideration, the alternative — relying exclusively on voluntary corporate action and market mechanisms — has demonstrably failed to deliver emissions reductions at the necessary pace. The urgency of the climate crisis justifies a more interventionist approach.

In conclusion, while a comprehensive response to climate change requires contributions from individuals, businesses, and civil society, governments must assume primary responsibility for creating the regulatory and financial conditions in which the transition to a sustainable economy can occur at the required speed and scale.""", 268),

    ("Is Technology Making Us Less Social?", "Technology", "evaluation", 7.5, """The proliferation of smartphones and social media platforms has fundamentally altered the way human beings interact with one another. While technology ostensibly connects people across vast distances, a growing chorus of researchers and social commentators contend that it is simultaneously eroding the quality of face-to-face relationships and fragmenting communities. This essay will examine both perspectives before reaching a considered conclusion.

Those who argue that technology diminishes sociality point to the increasingly observable phenomenon of physical co-presence combined with digital absence — people sitting together in restaurants while absorbed in their devices, or families sharing meals in silence, each engrossed in a separate screen. Sherry Turkle, a professor at MIT, has documented through extensive research how digital communication, while superficially connecting us, may in fact undermine our capacity for genuine empathy and deep conversation. The ability to curate our digital personas also encourages performative rather than authentic interaction, potentially leaving users feeling more isolated despite being constantly connected.

Conversely, technology has undeniably enabled forms of social connection that would otherwise be impossible. Individuals with social anxiety, physical disabilities, or geographical isolation may find that digital platforms provide essential communities and meaningful relationships. Moreover, messaging applications and video calls allow families and friendships to maintain bonds across continents in ways that previous generations could scarcely have imagined.

The truth, as is so often the case, lies somewhere between these polarised positions. Technology is not inherently antisocial — its effects depend entirely on how mindfully it is used. The challenge for contemporary societies is to cultivate digital literacy and intentional usage habits that harness technology's connective potential without sacrificing the irreplaceable richness of embodied human connection.

In conclusion, technology's impact on sociality is not predetermined but contingent on choices made by individuals, designers, and policymakers. Used mindfully, it can enrich human connection; used compulsively, it risks impoverishing it.""", 265),

    ("Should Governments Ban Junk Food Advertising to Children?", "Health", "reasoning", 7.5, """The relationship between food advertising targeted at children and the global childhood obesity epidemic has become an increasingly urgent public health concern. As rates of diet-related disease continue to rise at alarming rates, many health advocates argue that governments have not only the right but the obligation to restrict the marketing of unhealthy food products to minors. This essay contends that such restrictions are both justified and necessary.

The case for regulatory intervention rests on a fundamental asymmetry between the sophistication of modern marketing techniques and children's cognitive capacity to critically evaluate advertising. Neurological research confirms that children below the age of approximately eight are developmentally incapable of recognising the persuasive intent of advertising, rendering them exceptionally vulnerable to manipulation. When multinational food corporations deploy cartoon characters, celebrity endorsements, and gamification to promote nutritionally bankrupt products, they are essentially exploiting psychological vulnerabilities for commercial gain — a practice that is ethically indefensible.

The public health consequences of failing to act are severe. Childhood obesity is strongly associated with a range of serious conditions including type 2 diabetes, cardiovascular disease, and certain cancers. These conditions impose enormous costs not only on affected individuals and their families but on healthcare systems and national economies. Norway and the United Kingdom have both implemented restrictions on junk food advertising to children, with evidence suggesting positive effects on dietary behaviours.

Opponents of advertising restrictions frequently invoke principles of parental responsibility and market freedom. While parental guidance is undoubtedly important, it is unrealistic to expect parents to consistently counteract the multi-billion-dollar marketing budgets deployed by the food industry. Moreover, the costs of inaction are borne disproportionately by lower-income families, who are less able to afford healthy alternatives and more heavily targeted by aggressive marketing campaigns.

In conclusion, restricting junk food advertising to children represents a proportionate, evidence-based intervention that is fully justified by the scale of the public health crisis it seeks to address.""", 270),
]

added_essays = 0
for title, topic_name, question_type, band_score, content, word_count in essays_data:
    existing = db.query(Essay).filter(Essay.title == title).first()
    if not existing:
        e = Essay(
            title=title,
            topic_id=topics[topic_name].id,
            question_type=question_type,
            band_score=band_score,
            content=content,
            word_count=word_count,
            is_premium=False
        )
        db.add(e)
        added_essays += 1

db.commit()
print(f"✅ Essays: {added_essays} ta yangi qo'shildi")

# ─── GRAMMAR STRUCTURES ───────────────────────────────────
grammar_data = [
    ("Although / Even though", "Concession", "7", "Although + clause, + main clause",
     "Qarama-qarshi fikrni bildirish. Ikki jumlani birlashtiradi.",
     "Although technology has improved communication, it has also led to social isolation.",
     "Even though governments invest heavily in education, skill gaps remain prevalent.",
     "task2", False),

    ("While / Whereas", "Concession", "7", "While/Whereas + clause, + main clause",
     "Ikki fikrni taqqoslash. Bir vaqtda ikki narsa haqida gapirish.",
     "While some argue globalisation benefits developing nations, others contend it exacerbates inequality.",
     "Whereas urban residents enjoy better infrastructure, rural communities often lack services.",
     "task2", False),

    ("Despite / In spite of", "Concession", "8", "Despite/In spite of + noun/gerund, + main clause",
     "Biror narsaga qaramay degani. Noun yoki -ing bilan ishlatiladi.",
     "Despite significant investment in renewable energy, fossil fuels continue to dominate.",
     "In spite of widespread awareness, obesity rates have continued to rise.",
     "task2", False),

    ("Furthermore / Moreover / In addition", "Addition", "7", "Furthermore/Moreover, + additional point",
     "Qo'shimcha argument yoki fikr qo'shish uchun. Ko'p ishlatiladi.",
     "Furthermore, research demonstrates a strong correlation between education and economic prosperity.",
     "Moreover, the psychological benefits of exercise extend beyond physical health.",
     "both", False),

    ("Not only... but also", "Addition", "8", "Not only does/is + subject + verb, but it also + verb",
     "Ikkita muhim fikrni kuchaytirish. Inversiya bilan ishlatiladi.",
     "Not only does remote working reduce costs, but it also enhances employee productivity.",
     "Not only has globalisation accelerated growth, but it has also facilitated cultural exchange.",
     "task2", False),

    ("As a result / Consequently", "Cause & Effect", "7", "As a result/Consequently, + effect",
     "Sabab-natija bog'lanishini ifodalash. Paragraph boshida ishlatiladi.",
     "As a result of rapid urbanisation, many cities are struggling to provide adequate housing.",
     "Consequently, millions of people lack access to clean drinking water.",
     "both", False),

    ("This inevitably leads to", "Cause & Effect", "8", "This inevitably leads to + noun/gerund",
     "Muqarrar natijani ifodalash. 'inevitably' so'zi kuchli ta'sir qiladi.",
     "Excessive screen time inevitably leads to sleep deprivation.",
     "Unchecked deforestation inevitably leads to the collapse of ecosystems.",
     "task2", False),

    ("Compared to / In comparison with", "Comparison", "7", "Compared to + noun, + main clause",
     "Task 1 da ikki narsani taqqoslash. Juda ko'p ishlatiladi.",
     "Compared to 2010, the proportion of renewable energy users increased dramatically.",
     "In comparison with developed nations, developing countries consume less energy.",
     "task1", False),

    ("It is widely believed/argued that", "Opinion", "7", "It is widely believed/argued/accepted that + clause",
     "Umumiy fikrni bildirish. Shaxsiy fikrdan uzoqlashish imkonini beradi.",
     "It is widely believed that access to quality education is a fundamental human right.",
     "It is commonly argued that governments bear primary responsibility for environmental protection.",
     "task2", False),

    ("I would contend/argue that", "Opinion", "9", "I would contend/argue/maintain that + clause",
     "'I think' ning Band 9 varianti. Qat'iy pozitsiya bildiradi.",
     "I would contend that the benefits of globalisation are distributed profoundly unevenly.",
     "I would maintain that technological unemployment can be mitigated through proactive policy.",
     "task2", False),

    ("The extent to which", "Advanced", "9", "The extent to which + clause + determines/shapes + noun",
     "Akademik darajadagi murakkab struktura. Examinerga kuchli ta'sir qiladi.",
     "The extent to which social media influences political opinion remains contested.",
     "The extent to which governments prioritise growth over sustainability determines prosperity.",
     "task2", True),

    ("What is particularly striking is", "Advanced", "9", "What is particularly striking/significant is (that) + clause",
     "Diqqatni muhim fikrga jalb qilish. C2 darajasida.",
     "What is particularly striking is that inequality continues to widen despite economic growth.",
     "What is especially alarming is the rate at which biodiversity loss is accelerating.",
     "task2", True),

    ("It is no coincidence that", "Advanced", "9", "It is no coincidence that + clause",
     "Ikki hodisa o'rtasidagi bog'liqlikni ta'kidlash.",
     "It is no coincidence that countries with high literacy rates also boast strong economies.",
     "It is no coincidence that urban areas with good public transport report lower pollution.",
     "both", True),

    ("Admittedly... However", "Concession", "8", "Admittedly, + concession. However, + main argument.",
     "Qarshi tomonni tan olish, keyin o'z fikringizni kuchaytirish. Band 8 uchun zarur.",
     "Admittedly, economic growth can generate employment. However, the environmental cost is prohibitive.",
     "Admittedly, social media fosters connectivity. Nevertheless, its addictive nature poses risks.",
     "task2", False),

    ("A growing body of evidence suggests", "Academic", "8", "A growing body of evidence suggests/indicates that + clause",
     "Ilmiy isbotga tayanish uchun. Akademik uslubda juda samarali.",
     "A growing body of evidence suggests that social media exacerbates mental health issues.",
     "A growing body of research indicates that exercise reduces the risk of depression.",
     "task2", False),
]

added_grammar = 0
for item in grammar_data:
    title, category, band_level, structure, explanation_uz, ex1, ex2, task_type, is_premium = item
    existing = db.query(GrammarStructure).filter(GrammarStructure.title == title).first()
    if not existing:
        g = GrammarStructure(
            title=title, category=category, band_level=band_level,
            structure=structure, explanation_uz=explanation_uz,
            example_1=ex1, example_2=ex2, task_type=task_type,
            is_premium=is_premium, order_num=0
        )
        db.add(g)
        added_grammar += 1

db.commit()
print(f"✅ Grammar structures: {added_grammar} ta yangi qo'shildi")

# ─── SPEAKING QUESTIONS ───────────────────────────────────
speaking_data = [
    (1, "Technology", "Do you use social media regularly?", False),
    (1, "Technology", "How has technology changed communication in your country?", False),
    (1, "Education", "Did you enjoy studying at school?", False),
    (1, "Education", "What subject did you find most challenging at school?", False),
    (1, "Environment", "Do you think people care enough about the environment?", False),
    (1, "Health", "Do you do any sports or exercise?", False),
    (1, "Society", "What do you do in your free time?", False),
    (2, "Places", "Describe a place you have visited that you found particularly interesting.", False),
    (2, "People", "Describe a person who has had a great influence on you.", False),
    (2, "Technology", "Describe a piece of technology you find particularly useful.", False),
    (3, "Technology", "Do you think artificial intelligence will replace human workers in the future?", False),
    (3, "Environment", "What can governments do to encourage people to be more environmentally friendly?", False),
    (3, "Education", "How important is university education in today's society?", False),
    (3, "Society", "Do you think social media has had a positive or negative effect on society?", False),
]

added_speaking = 0
for part, topic_name, question, is_premium in speaking_data:
    existing = db.query(SpeakingQuestion).filter(SpeakingQuestion.question == question).first()
    if not existing:
        sq = SpeakingQuestion(
            part=part, topic_id=topics[topic_name].id,
            question=question, is_premium=is_premium
        )
        db.add(sq)
        added_speaking += 1

db.commit()
print(f"✅ Speaking questions: {added_speaking} ta yangi qo'shildi")

db.close()

print("\n🎉 Barcha kontent muvaffaqiyatli qo'shildi!")
print(f"📚 Topics: {len(topics)}")
print(f"🧠 Vocabulary: {added_vocab} ta yangi")
print(f"✍️  Essays: {added_essays} ta yangi")
print(f"📐 Grammar: {added_grammar} ta yangi")
print(f"🎤 Speaking: {added_speaking} ta yangi")