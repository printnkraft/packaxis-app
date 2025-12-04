"""
Create initial FAQ entries for PackAxis
Run this script to populate FAQs with common questions
Usage: python create_faqs.py
"""

import os
import django

# Setup Django environment first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'packaxis_app.settings')
django.setup()

from core.models import FAQ

# FAQ data
FAQS = [
    {
        'question': "What's your minimum order quantity?",
        'answer': '<p>Our minimum order quantity is <strong>10,000 pieces</strong>. This allows us to offer competitive pricing while maintaining the high quality standards our customers expect. Bulk ordering also provides the best value per unit and ensures you have adequate inventory for your business needs.</p>',
        'order': 1,
        'category': 'Ordering',
    },
    {
        'question': "Do you ship across Canada?",
        'answer': '<p><strong>Yes!</strong> We provide shipping services across all of Canada. Whether you\'re in Toronto, Vancouver, Montreal, Calgary, or any other city, we can deliver your custom paper bags to your location. Shipping costs and delivery times vary by destination and order size. Contact us for a detailed shipping quote for your specific location.</p>',
        'order': 2,
        'category': 'Shipping',
    },
    {
        'question': "How long does custom printing take?",
        'answer': '<p>Custom printing typically takes <strong>10-12 business days</strong> from the time your artwork is approved and your order is confirmed. This timeline includes:</p><ul><li>Artwork review and approval (1-2 days)</li><li>Production and printing (7-9 days)</li><li>Quality control and packaging (1 day)</li></ul><p>Rush orders may be available for an additional fee. Please contact us to discuss expedited options if you have a tight deadline.</p>',
        'order': 3,
        'category': 'Customization',
    },
    {
        'question': "What paper GSM should I choose?",
        'answer': '<p>The right GSM (grams per square meter) depends on your intended use:</p><ul><li><strong>60-80 GSM:</strong> Lightweight and economical. Best for light items like clothing, gift wrapping, and promotional events. Can hold up to 2 kg comfortably.</li><li><strong>90-100 GSM:</strong> Our most popular option. Balances durability and cost. Suitable for most retail applications and can hold 5-8 kg.</li><li><strong>120+ GSM:</strong> Premium, heavy-duty bags with excellent strength. Ideal for heavier items, luxury retail, and customers who want a premium feel. Can hold 10+ kg.</li></ul><p>We\'re happy to provide samples so you can test different GSM options with your actual products before placing a bulk order.</p>',
        'order': 4,
        'category': 'Product Specifications',
    },
    {
        'question': "Are your bags biodegradable?",
        'answer': '<p><strong>Yes!</strong> All our paper bags are 100% biodegradable and environmentally friendly. Made from kraft paper, they naturally decompose within 2-6 weeks when exposed to the elements, unlike plastic bags which can take hundreds of years.</p><p>Our bags are also:</p><ul><li><strong>Recyclable:</strong> Can be recycled 5-7 times through standard paper recycling programs</li><li><strong>Compostable:</strong> Safe for composting facilities</li><li><strong>Sustainable:</strong> Made from renewable resources with FSC certification options available</li><li><strong>Chemical-free:</strong> No harmful additives or coatings</li></ul><p>By choosing our paper bags, you\'re making an environmentally responsible choice that aligns with Canada\'s plastic reduction initiatives.</p>',
        'order': 5,
        'category': 'Sustainability',
    },
    {
        'question': "Can I see samples before ordering?",
        'answer': '<p>Absolutely! We encourage customers to request samples before placing large orders. We can provide:</p><ul><li><strong>Blank samples:</strong> Unprinted bags in various sizes and GSM weights (free)</li><li><strong>Printed samples:</strong> Previous work examples to show print quality</li><li><strong>Custom sample run:</strong> A small batch with your design (additional cost)</li></ul><p>Contact us to request samples, and we\'ll ship them to you so you can evaluate quality, size, and weight capacity with your actual products.</p>',
        'order': 6,
        'category': 'Ordering',
    },
    {
        'question': "What customization options are available?",
        'answer': '<p>We offer extensive customization options:</p><p><strong>Sizes:</strong> 13 standard sizes from 5" to 18" width, or custom dimensions</p><p><strong>Printing:</strong></p><ul><li>1-4 color flexographic printing</li><li>Full-color digital printing</li><li>Hot stamping and foil printing</li><li>Inside and outside printing</li></ul><p><strong>Handle Options:</strong></p><ul><li>Twisted paper handles (standard)</li><li>Flat paper handles (reinforced)</li><li>Cotton rope handles (premium)</li><li>Ribbon handles (luxury)</li></ul><p><strong>Paper Options:</strong> Natural kraft, white kraft, colored paper, recycled content</p><p><strong>Finishes:</strong> Matte, gloss, or textured finishes available</p>',
        'order': 7,
        'category': 'Customization',
    },
    {
        'question': "What file format do you need for artwork?",
        'answer': '<p>For best printing results, please provide:</p><ul><li><strong>Vector files:</strong> AI, EPS, or PDF (preferred)</li><li><strong>Raster files:</strong> High-resolution PNG or JPG (300 DPI minimum)</li><li><strong>Color mode:</strong> CMYK (not RGB)</li><li><strong>Bleed:</strong> Include 3mm bleed on all edges</li><li><strong>Fonts:</strong> Convert all text to outlines/curves</li></ul><p>Don\'t have print-ready artwork? No problem! Our design team can help optimize your files or create designs from scratch. We provide free design consultation and digital proofs before production.</p>',
        'order': 8,
        'category': 'Customization',
    },
    {
        'question': "Do you offer rush production?",
        'answer': '<p>Yes, rush production is available depending on our current production schedule and order complexity. Rush orders typically add 3-5 business days to standard production, but we can accommodate faster turnarounds when possible.</p><p>Rush production incurs an additional fee based on order size and timeline requirements. Contact us as soon as possible with your deadline, and we\'ll do our best to accommodate your needs.</p><p>For the fastest service, consider:</p><ul><li>Using standard sizes (eliminates custom die-cutting)</li><li>Limiting colors (1-2 colors print faster than full color)</li><li>Having print-ready artwork approved quickly</li></ul>',
        'order': 9,
        'category': 'Production',
    },
    {
        'question': "What payment methods do you accept?",
        'answer': '<p>We accept multiple payment methods for your convenience:</p><ul><li><strong>Bank Transfer/Wire Transfer:</strong> For large orders (preferred)</li><li><strong>Credit Cards:</strong> Visa, Mastercard, American Express</li><li><strong>Company Check:</strong> For established business accounts</li><li><strong>Payment Terms:</strong> Net 30 available for approved accounts</li></ul><p>A 50% deposit is typically required before production begins, with the balance due before shipping. We can discuss alternative payment arrangements for large or recurring orders.</p>',
        'order': 10,
        'category': 'Ordering',
    },
]

def create_faqs():
    """Create FAQ entries"""
    print("Creating FAQ entries...")
    
    created_count = 0
    updated_count = 0
    
    for faq_data in FAQS:
        faq, created = FAQ.objects.update_or_create(
            question=faq_data['question'],
            defaults={
                'answer': faq_data['answer'],
                'order': faq_data['order'],
                'category': faq_data['category'],
                'is_active': True,
            }
        )
        
        if created:
            print(f"✓ Created: {faq.question}")
            created_count += 1
        else:
            print(f"  Updated: {faq.question}")
            updated_count += 1
    
    print(f"\n✓ FAQ setup complete!")
    print(f"Created: {created_count}")
    print(f"Updated: {updated_count}")
    print(f"Total FAQs: {FAQ.objects.count()}")
    print(f"Active FAQs: {FAQ.objects.filter(is_active=True).count()}")

if __name__ == '__main__':
    create_faqs()
