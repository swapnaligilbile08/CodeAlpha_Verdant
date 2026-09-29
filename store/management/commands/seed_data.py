import random
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from store.models import Category, Product, Review

def category_photo(filename):
    return f"{settings.STATIC_URL}img/categories/{filename}"


def product_photo(filename):
    return f"{settings.STATIC_URL}img/products/{filename}"


CATEGORIES = [
    {"name": "Indoor Plants", "photo": category_photo("indoor-plants.jpg"),
     "description": "Low-maintenance greenery for every room."},
    {"name": "Outdoor Plants", "photo": category_photo("outdoor-plants.jpg"),
     "description": "Hardy plants for balconies, patios and gardens."},
    {"name": "Succulents & Cacti", "photo": category_photo("succulents-cacti.webp"),
     "description": "Drought-tolerant plants that forgive a missed watering."},
    {"name": "Pots & Accessories", "photo": category_photo("pots-accessories.png"),
     "description": "Planters, saucers, soil and the tools to keep it all alive."},
    {"name": "Gift Plants", "photo": category_photo("gift-plants.jpg"),
     "description": "Beautifully packaged plants for birthdays and housewarmings."},
    {"name": "Care & Maintenance", "photo": category_photo("care-and-maintenance.jpg"),
     "description": "Fertilisers, pruning shears and everything care-related."},
    {"name": "Flowering Plants", "photo": category_photo("flowering-plants.avif"),
     "description": "Colour and blooms for every season."},
    {"name": "Air-Purifying Plants", "photo": category_photo("air-purifying-plants.webp"),
     "description": "NASA Clean Air Study favourites for bedrooms and offices."},
    {"name": "Bonsai & Ornamental Trees", "photo": category_photo("bonsai-trees.avif"),
     "description": "Sculpted miniature trees for a calm, focal statement piece."},
    {"name": "Herbs & Kitchen Garden", "photo": category_photo("herbs-kitchen-garden.jpg"),
     "description": "Fresh herbs you can actually cook with, grown on a windowsill."},
    {"name": "Trailing & Hanging Plants", "photo": category_photo("trailing-hanging-plants.jpg"),
     "description": "Vines and cascading foliage for shelves, hooks and macramé."},
]

PRODUCTS = [
    # -------- Indoor Plants --------
    dict(cat="Indoor Plants", name="Monstera Deliciosa", price="1499", compare="1899", stock=24,
         image=product_photo("monstera-deliciosa.jpg"), featured=True, deal=False,
         desc="Big split leaves, the plant everyone recognizes. Comes in a 6-inch pot.",
         care="Bright, indirect light. Water when the top 2 inches of soil are dry, roughly every 7–10 days."),
    dict(cat="Indoor Plants", name="Snake Plant (Sansevieria)", price="899", compare=None, stock=40,
         image=product_photo("snake-plant.jpg"), featured=True, deal=True,
         desc="Tough, low-light plant that's hard to kill. A good first plant.",
         care="Tolerates low to bright indirect light. Water every 2–3 weeks, less in winter."),
    dict(cat="Indoor Plants", name="Golden Pothos", price="599", compare="749", stock=55,
         image=product_photo("golden-pothos.jpg"), featured=True, deal=True,
         desc="Fast-growing trailing vine with heart-shaped leaves. Easy to keep alive.",
         care="Low to bright indirect light. Let soil dry between waterings."),
    dict(cat="Indoor Plants", name="Fiddle Leaf Fig", price="2199", compare=None, stock=12,
         image=product_photo("fiddle-leaf-fig.jpg"), featured=True, deal=False,
         desc="Big violin-shaped leaves on a tall stem. A statement plant for a bright corner.",
         care="Bright indirect light, consistent watering. Dislikes being moved once settled."),
    dict(cat="Indoor Plants", name="ZZ Plant", price="1099", compare="1299", stock=30,
         image=product_photo("zz-plant.jpg"), featured=False, deal=True,
         desc="Glossy leaves, barely needs any care. Good for offices and dim hallways.",
         care="Low to bright indirect light. Water every 2–3 weeks."),
    dict(cat="Indoor Plants", name="Peace Lily", price="999", compare=None, stock=28,
         image=product_photo("peace-lily.jpg"), featured=False, deal=False,
         desc="White blooms, glossy leaves. Droops when it's thirsty, so it's easy to read.",
         care="Medium to low indirect light. Keep soil consistently moist, not soggy."),
    dict(cat="Indoor Plants", name="Areca Palm", price="1799", compare=None, stock=15,
         image=product_photo("areca-palm.jpg"), featured=False, deal=False,
         desc="Feathery palm fronds that bring a tropical feel to a room.",
         care="Bright indirect light. Water when the top inch of soil is dry."),
    dict(cat="Indoor Plants", name="Spider Plant", price="499", compare="599", stock=48,
         image=product_photo("spider-plant.jpg"), featured=False, deal=False,
         desc="Easy grower with striped leaves and baby plantlets you can share.",
         care="Bright, indirect light. Water weekly, let soil dry slightly between."),

    # -------- Outdoor Plants --------
    dict(cat="Outdoor Plants", name="Bougainvillea", price="649", compare=None, stock=20,
         image=product_photo("bougainvillea.jpg"), featured=False, deal=False,
         desc="Bright magenta blooms, great for a sunny balcony or fence.",
         care="Full sun. Water deeply, then let soil dry out — thrives on a little neglect."),
    dict(cat="Outdoor Plants", name="Hibiscus", price="799", compare="949", stock=18,
         image=product_photo("hibiscus.jpg"), featured=False, deal=True,
         desc="Big trumpet flowers that open fresh each morning in warm weather.",
         care="Full sun, regular watering. Feed monthly during bloom season."),
    dict(cat="Outdoor Plants", name="Jasmine Vine", price="549", compare=None, stock=25,
         image=product_photo("jasmine-vine.jpeg"), featured=False, deal=False,
         desc="Fragrant white flowers, lovely on a courtyard in summer.",
         care="Full to partial sun. Keep soil consistently moist during flowering."),
    dict(cat="Outdoor Plants", name="Curry Leaf Tree, Garden Size", price="399", compare=None, stock=35,
         image=product_photo("curry-leaf-tree.jpg"), featured=False, deal=False,
         desc="A bigger curry leaf plant for garden beds or large pots.",
         care="Full sun, well-draining soil. Water when topsoil feels dry."),

    # -------- Flowering Plants --------
    dict(cat="Flowering Plants", name="Rose Plant, Red", price="349", compare="429", stock=30,
         image=product_photo("rose-red.jpg"), featured=True, deal=False,
         desc="Classic red rose bush, grafted for bigger, longer-lasting blooms.",
         care="Full sun, at least 5–6 hours daily. Water deeply 2–3 times a week; prune after each flush."),
    dict(cat="Flowering Plants", name="Marigold, Mixed Colours", price="149", compare=None, stock=60,
         image=product_photo("marigold.jpg"), featured=False, deal=True,
         desc="Cheerful orange and yellow flowers that bloom almost nonstop.",
         care="Full sun. Water when topsoil is dry; deadhead spent flowers to keep it blooming."),
    dict(cat="Flowering Plants", name="Chandni (Crepe Jasmine)", price="199", compare="249", stock=22,
         image=product_photo("chandni.jpg"), featured=False, deal=False,
         desc="White star-shaped flowers with a light scent.",
         care="Full to partial sun. Keep soil lightly moist; tolerates light pruning well."),
    dict(cat="Flowering Plants", name="Rajnigandha (Tuberose)", price="179", compare=None, stock=26,
         image=product_photo("rajnigandha.jpg"), featured=False, deal=False,
         desc="Tall, fragrant white flower spikes, often used for garlands.",
         care="Full sun, well-draining soil. Water regularly during the growing season, less once dormant."),

    # -------- Air-Purifying Plants --------
    dict(cat="Air-Purifying Plants", name="Aloe Vera", price="249", compare="299", stock=45,
         image=product_photo("aloe-vera.jpg"), featured=True, deal=False,
         desc="Easy succulent with gel-filled leaves, handy for minor skin soothing.",
         care="Bright light, some direct sun. Water deeply, then let soil dry out completely."),
    dict(cat="Air-Purifying Plants", name="Rubber Plant (Ficus Elastica)", price="899", compare=None, stock=20,
         image=product_photo("rubber-plant.jpg"), featured=False, deal=False,
         desc="Big glossy leaves, one of the better air-purifying houseplants.",
         care="Bright indirect light. Water when the top inch of soil is dry; wipe leaves to keep them dust-free."),
    dict(cat="Air-Purifying Plants", name="Boston Fern", price="399", compare="479", stock=28,
         image=product_photo("boston-fern.jpg"), featured=False, deal=True,
         desc="Feathery fronds that like a humid spot, like a bathroom.",
         care="Bright indirect light, high humidity. Keep soil consistently moist, never soggy."),
    dict(cat="Air-Purifying Plants", name="Chinese Evergreen (Aglaonema)", price="549", compare=None, stock=24,
         image=product_photo("chinese-evergreen.jpg"), featured=False, deal=False,
         desc="Patterned leaves that handle low light well.",
         care="Low to medium indirect light. Water when the top inch of soil feels dry."),

    # -------- Succulents & Cacti --------
    dict(cat="Succulents & Cacti", name="Echeveria Rosette", price="349", compare="429", stock=60,
         image=product_photo("echeveria-rosette.jpg"), featured=True, deal=True,
         desc="Neat blue-green rosette, the succulent everyone photographs first.",
         care="Bright light, ideally some direct sun. Water only when soil is fully dry."),
    dict(cat="Succulents & Cacti", name="Barrel Cactus", price="449", compare=None, stock=22,
         image=product_photo("barrel-cactus.jpg"), featured=False, deal=False,
         desc="Classic round, ribbed cactus. Needs almost nothing from you.",
         care="Full sun. Water sparingly, roughly once a month."),
    dict(cat="Succulents & Cacti", name="String of Pearls", price="599", compare="699", stock=26,
         image=product_photo("string-of-pearls.jpg"), featured=False, deal=False,
         desc="Trailing pea-like leaves, great spilling over a shelf.",
         care="Bright light. Water deeply, then let dry completely — avoid wetting the leaves."),
    dict(cat="Succulents & Cacti", name="Haworthia Zebra Plant", price="399", compare=None, stock=33,
         image=product_photo("haworthia-zebra.jpg"), featured=False, deal=False,
         desc="Small striped rosettes, a good little desk plant.",
         care="Bright indirect light. Water every 2–3 weeks."),

    # -------- Bonsai & Ornamental Trees --------
    dict(cat="Bonsai & Ornamental Trees", name="Ficus Bonsai", price="1299", compare="1799", stock=10,
         image=product_photo("ficus-bonsai.avif"), featured=True, deal=True,
         desc="Hand-trained miniature fig tree, a calm centrepiece for a desk.",
         care="Bright indirect light, some direct morning sun. Water when the top of the soil feels dry."),
    dict(cat="Bonsai & Ornamental Trees", name="Araucaria (Christmas Tree Plant)", price="649", compare=None, stock=16,
         image=product_photo("araucaria.jpg"), featured=False, deal=False,
         desc="Soft, tiered foliage that looks like a mini pine tree.",
         care="Bright indirect light. Water when the top inch of soil is dry; avoid direct hot afternoon sun."),
    dict(cat="Bonsai & Ornamental Trees", name="Jade Plant Bonsai-Style", price="549", compare="649", stock=18,
         image=product_photo("jade-bonsai.jpg"), featured=False, deal=False,
         desc="Thick-trunked jade plant shaped like a bonsai. Hard to overwater.",
         care="Bright light, some direct sun. Water only when soil is fully dry."),

    # -------- Herbs & Kitchen Garden --------
    dict(cat="Herbs & Kitchen Garden", name="Curry Leaf Plant", price="249", compare=None, stock=32,
         image=product_photo("curry-leaf-plant.jpg"), featured=False, deal=False,
         desc="Fresh curry leaves whenever you need them, right on a sunny windowsill.",
         care="Full sun, well-draining soil. Water when topsoil feels dry."),
    dict(cat="Herbs & Kitchen Garden", name="Lemongrass", price="199", compare="249", stock=27,
         image=product_photo("lemongrass.jpg"), featured=False, deal=True,
         desc="Citrusy stalks for tea and cooking. A tough, fast grower.",
         care="Full sun. Water regularly, allowing soil to dry slightly between waterings."),
    dict(cat="Herbs & Kitchen Garden", name="Mint Plant", price="129", compare=None, stock=40,
         image=product_photo("mint-plant.jpg"), featured=False, deal=False,
         desc="Fresh mint for chutneys, tea and mojitos. Grows fast.",
         care="Partial to full sun. Keep soil consistently moist; pinch tips to encourage bushiness."),
    dict(cat="Herbs & Kitchen Garden", name="Papaya Plant", price="199", compare="299", stock=15,
         image=product_photo("papaya-plant.jpg"), featured=False, deal=False,
         desc="A young papaya sapling for a sunny garden spot.",
         care="Full sun, well-draining soil. Water regularly; avoid waterlogging the roots."),

    # -------- Trailing & Hanging Plants --------
    dict(cat="Trailing & Hanging Plants", name="Money Plant (Epipremnum)", price="149", compare="199", stock=50,
         image=product_photo("money-plant.jpg"), featured=True, deal=True,
         desc="Classic trailing vine, grows in soil or water. Said to bring good luck.",
         care="Low to bright indirect light. Water when the top inch of soil is dry, or keep in water year-round."),
    dict(cat="Trailing & Hanging Plants", name="String of Hearts", price="449", compare=None, stock=20,
         image=product_photo("string-of-hearts.jpg"), featured=False, deal=False,
         desc="Thin vines with tiny heart-shaped leaves, nice in a hanging pot.",
         care="Bright light. Water deeply, then let dry completely between waterings."),
    dict(cat="Trailing & Hanging Plants", name="Devil's Ivy, Marble Queen", price="399", compare="499", stock=24,
         image=product_photo("marble-queen-pothos.jpg"), featured=False, deal=True,
         desc="Variegated pothos, brighter than the plain green version.",
         care="Bright indirect light keeps the variegation strongest. Let soil dry between waterings."),

    # -------- Pots & Accessories --------
    dict(cat="Pots & Accessories", name="Terracotta Planter, 8-inch", price="349", compare=None, stock=70,
         image=product_photo("terracotta-planter.jpg"), featured=False, deal=False,
         desc="Classic unglazed terracotta pot with a drainage hole and saucer.",
         care="Hand-wash only; terracotta is porous and can crack in a dishwasher."),
    dict(cat="Pots & Accessories", name="Ceramic Planter, Matte White", price="599", compare="749", stock=45,
         image=product_photo("ceramic-planter.jpg"), featured=True, deal=True,
         desc="Clean matte-white pot with hidden drainage and a bamboo tray.",
         care="Wipe clean with a damp cloth."),
    dict(cat="Pots & Accessories", name="Hanging Macramé Planter", price="449", compare=None, stock=38,
         image=product_photo("macrame-planter.jpg"), featured=False, deal=False,
         desc="Hand-knotted cotton hanger that holds a 6-inch pot.",
         care="Spot clean; keep dry to prevent mildew."),
    dict(cat="Pots & Accessories", name="Potting Mix, 5L Bag", price="299", compare=None, stock=90,
         image=product_photo("potting-mix.jpg"), featured=False, deal=False,
         desc="Well-draining potting mix with perlite and coco coir.",
         care="Store in a dry place; use within 12 months of opening."),

    # -------- Gift Plants --------
    dict(cat="Gift Plants", name="Orchid Gift Box", price="1299", compare="1599", stock=18,
         image=product_photo("orchid-gift-box.jpg"), featured=True, deal=True,
         desc="Orchid in a gift-wrapped pot with a card slot. Ready to send.",
         care="Bright indirect light. Water with 3 ice cubes weekly, or a splash of water every 7–10 days."),
    dict(cat="Gift Plants", name="Lucky Bamboo Arrangement", price="699", compare=None, stock=24,
         image=product_photo("lucky-bamboo.jpg"), featured=False, deal=False,
         desc="Braided bamboo in a glass vase with stones. A classic housewarming gift.",
         care="Keep roots submerged in water; change water every 1–2 weeks."),
    dict(cat="Gift Plants", name="Succulent Trio Gift Set", price="549", compare="649", stock=32,
         image=product_photo("succulent-gift-trio.jpg"), featured=False, deal=False,
         desc="Three mini succulents in matching pots, boxed and ribboned.",
         care="Bright light. Water sparingly, roughly every 2 weeks."),

    # -------- Care & Maintenance --------
    dict(cat="Care & Maintenance", name="Stainless Steel Pruning Shears", price="399", compare=None, stock=50,
         image=product_photo("pruning-shears.jpg"), featured=False, deal=False,
         desc="Sharp, comfortable shears for trimming and taking cuttings.",
         care="Wipe blades after each use to prevent rust."),
    dict(cat="Care & Maintenance", name="Copper Watering Can, 1.5L", price="799", compare="949", stock=27,
         image=product_photo("watering-can.jpg"), featured=False, deal=False,
         desc="Long-spout can that reaches hanging planters without the mess.",
         care="Hand wash; dry to preserve the finish."),
    dict(cat="Care & Maintenance", name="Liquid Plant Food, 250ml", price="349", compare=None, stock=65,
         image=product_photo("plant-food.jpg"), featured=False, deal=False,
         desc="Gentle liquid fertiliser — a few drops every couple of weeks.",
         care="Store away from direct sunlight."),
    dict(cat="Care & Maintenance", name="Moisture Meter", price="499", compare="599", stock=40,
         image=product_photo("moisture-meter.jpg"), featured=False, deal=True,
         desc="Probe that reads soil moisture, so you know exactly when to water.",
         care="No batteries required; rinse the probe after use."),
]

REVIEW_COMMENTS = [
    (5, "Arrived healthy, looks great."),
    (5, "New leaf already, loving it."),
    (4, "Good quality, shipping was slow."),
    (5, "Super easy to take care of."),
    (3, "Smaller than I expected."),
    (4, "Solid, ordering again."),
    (5, "Packed well, zero damage."),
    (4, "Settling in nicely so far."),
]


class Command(BaseCommand):
    help = "Seed the database with plant categories, products and demo reviews."

    def add_arguments(self, parser):
        parser.add_argument("--flush-products", action="store_true",
                             help="Delete existing categories/products before reseeding.")

    def handle(self, *args, **options):
        if options["flush_products"]:
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write("Cleared existing categories and products.")

        cat_objs = {}
        for c in CATEGORIES:
            obj, created = Category.objects.get_or_create(
                name=c["name"], defaults={"photo_url": c["photo"], "description": c["description"]}
            )
            if not created:
                obj.photo_url = c["photo"]
                obj.description = c["description"]
                obj.save()
            cat_objs[c["name"]] = obj
        self.stdout.write(self.style.SUCCESS(f"Categories ready: {len(cat_objs)}"))

        # A few demo reviewers, so seeded products have believable ratings.
        reviewers = []
        for i in range(1, 5):
            user, _ = User.objects.get_or_create(
                username=f"demo_reviewer{i}", defaults={"email": f"reviewer{i}@example.com"}
            )
            if not user.has_usable_password():
                user.set_password("PlantLover123!")
                user.save()
            reviewers.append(user)

        created_count = 0
        for p in PRODUCTS:
            product, created = Product.objects.update_or_create(
                name=p["name"],
                defaults=dict(
                    category=cat_objs[p["cat"]],
                    description=p["desc"],
                    care_notes=p["care"],
                    price=Decimal(p["price"]),
                    compare_at_price=Decimal(p["compare"]) if p["compare"] else None,
                    image_url=p["image"],
                    stock=p["stock"],
                    is_featured=p["featured"],
                    is_deal_of_the_day=p["deal"],
                ),
            )
            if created:
                created_count += 1
                sample = random.sample(reviewers, k=random.randint(1, len(reviewers)))
                for reviewer in sample:
                    rating, comment = random.choice(REVIEW_COMMENTS)
                    Review.objects.get_or_create(
                        product=product, user=reviewer,
                        defaults={"rating": rating, "comment": comment},
                    )

        self.stdout.write(self.style.SUCCESS(
            f"Products ready: {Product.objects.count()} total ({created_count} newly created)."
        ))
        self.stdout.write(self.style.SUCCESS("Seeding complete."))
