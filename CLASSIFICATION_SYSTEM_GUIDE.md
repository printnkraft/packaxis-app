# Product Classification System Guide

## Overview
PackAxis now includes a comprehensive product classification system similar to Shopify, with hierarchical categories/industries and flexible tagging.

---

## 🏗️ **Hierarchical Categories**

### What's New
- **Parent-Child Relationships**: Categories can now have subcategories with unlimited nesting depth
- **Unique Slugs per Level**: Slug only needs to be unique within the same parent level
- **Automatic Navigation**: Methods for getting ancestors, descendants, and full path

### Example Structure
```
Paper Bags (parent=None)
├── Shopping Bags (parent=Paper Bags)
│   ├── Brown Kraft (parent=Shopping Bags)
│   └── White Paper (parent=Shopping Bags)
└── Specialty Bags (parent=Paper Bags)
    ├── Custom Branded (parent=Specialty Bags)
    └── Gift Bags (parent=Specialty Bags)
```

### How to Create Nested Categories

1. **Admin Interface**: `/superusers/core/productcategory/`
   - Create a parent category first (leave "Parent" field empty)
   - Create subcategories and select the parent from dropdown
   - Admin displays hierarchy with indentation

2. **Methods Available**:
   ```python
   category = ProductCategory.objects.get(slug='brown-kraft')
   
   # Get all parents up to root
   ancestors = category.get_ancestors()  # [Paper Bags, Shopping Bags]
   
   # Get full path
   path = category.get_full_path()  # "Paper Bags > Shopping Bags > Brown Kraft"
   
   # Get nesting level
   level = category.level  # 2 (0=root, 1=first child, etc.)
   
   # Get all children recursively
   descendants = category.get_descendants(include_self=True)
   ```

3. **Admin Features**:
   - ✅ Hierarchical display with indentation
   - ✅ Filter by parent category
   - ✅ Autocomplete search for parent selection
   - ✅ Shows product count per category

---

## 🏢 **Hierarchical Industries**

### What's New
- Same hierarchical structure as categories
- Perfect for nested industry classifications

### Example Structure
```
Food Service (parent=None)
├── Restaurants (parent=Food Service)
│   ├── Fast Food (parent=Restaurants)
│   ├── Fine Dining (parent=Restaurants)
│   └── Cafes (parent=Restaurants)
├── Catering (parent=Food Service)
└── Food Trucks (parent=Food Service)

Retail (parent=None)
├── Fashion Boutiques (parent=Retail)
├── Grocery Stores (parent=Retail)
└── Electronics (parent=Retail)
```

### How to Use

1. **Admin Interface**: `/superusers/core/industry/`
   - Same workflow as categories
   - Set parent for nested sub-industries
   - Admin displays with indentation

2. **Methods** (same as categories):
   ```python
   industry = Industry.objects.get(title='Fast Food')
   
   ancestors = industry.get_ancestors()  # [Food Service, Restaurants]
   path = industry.get_full_path()  # "Food Service > Restaurants > Fast Food"
   level = industry.level  # 2
   ```

---

## 🏷️ **Product Tags System**

### What's New (Similar to Shopify Tags)
- **Flat Structure**: Tags are non-hierarchical for maximum flexibility
- **Colored Tags**: Each tag has a customizable color
- **Many-to-Many**: Products can have multiple tags, tags can be on multiple products
- **Filtering**: Filter products by tags in admin and (future) frontend

### Example Tags
- `Eco-Friendly` (green)
- `Bulk Discount Available` (blue)
- `Custom Printing` (purple)
- `Food Safe` (orange)
- `Made in USA` (red)
- `Bestseller` (gold)
- `New Arrival` (teal)

### How to Create Tags

1. **Admin Interface**: `/superusers/core/tag/`
   - Click "Add Tag"
   - Enter name (auto-generates slug)
   - Choose color (hex format, e.g., `#3B82F6`)
   - Add optional description
   - Set order and active status

2. **Admin Features**:
   - ✅ Colored tag preview in list view
   - ✅ Shows product count per tag
   - ✅ Search by name, slug, description
   - ✅ Order tags for display priority

### How to Add Tags to Products

1. **Product Admin**: `/superusers/core/product/`
   - Edit any product
   - Scroll to "Basic Information" section
   - Find "Tags" field with filter_horizontal widget
   - Move tags from "Available" to "Chosen" column
   - Save product

2. **View Product Tags**:
   - Product list displays tags with colors
   - Shows first 5 tags, indicates if more exist
   - Filter products by tag using right sidebar

---

## 📊 **Admin Interface Guide**

### Product Categories (`/superusers/core/productcategory/`)
**List View:**
- Image preview
- **Title with indentation** (shows hierarchy level)
- Parent category
- Product count
- Order, Active status

**Filters:**
- Is active
- Parent category
- Created date

**Add/Edit:**
- Set parent for subcategories
- All existing fields remain
- Autocomplete for parent selection

---

### Industries (`/superusers/core/industry/`)
**List View:**
- Image preview
- **Title with indentation** (shows hierarchy level)
- Parent industry
- URL
- Order, Active status

**Filters:**
- Is active
- Parent industry
- Created date

---

### Products (`/superusers/core/product/`)
**List View:**
- Now shows **Tags column** with colored badges
- Filter by tags in right sidebar
- Search includes tag names

**Add/Edit:**
- **Tags field** in Basic Information section
- Use filter_horizontal widget (dual listbox)
- Select multiple tags easily

---

### Tags (`/superusers/core/tag/`)
**List View:**
- **Colored tag preview**
- Name, slug
- **Product count** (usage stats)
- Order, Active status

**Add/Edit:**
- Name (required, unique)
- Slug (auto-generated)
- Color (hex format, default: #3B82F6)
- Description (optional)
- Order, Active status

---

## 🔧 **Technical Details**

### Database Schema Changes

**Migration 0024** adds:
- `Tag` model with fields: name, slug, color, description, order, is_active
- `Product.tags` M2M relationship
- `ProductCategory.parent` ForeignKey (self-reference)
- `Industry.parent` ForeignKey (self-reference)
- `unique_together` on ProductCategory: (slug, parent)
- Indexes for performance

### Model Methods

**ProductCategory & Industry:**
```python
.get_ancestors()        # List of parent objects up to root
.get_descendants()      # List of all children recursively
.get_full_path()        # String like "Parent > Child > Grandchild"
.level                  # Integer nesting level (0=root)
```

**Tag:**
```python
.get_product_count()    # Number of active products with this tag
```

---

## 🚀 **Frontend Integration (Future)**

### URL Patterns for Nested Categories
```
/product/paper-bags/                           # Root category
/product/paper-bags/shopping-bags/             # Subcategory
/product/paper-bags/shopping-bags/brown-kraft/ # Product or sub-subcategory
```

### Tag Filtering
```
/products/?tags=eco-friendly,bulk-discount     # Multi-tag filter
/products/?tag=bestseller                      # Single tag filter
```

### Breadcrumbs with Full Hierarchy
```
Home > Paper Bags > Shopping Bags > Brown Kraft > Standard Shopping Bags
```

---

## ✅ **Best Practices**

### Categories
1. **Keep it simple**: Start with 2-3 levels max
2. **Consistent naming**: Use clear, descriptive names
3. **Order matters**: Set order values to control display sequence
4. **Don't duplicate**: Use parent-child relationships instead of similar flat categories

### Industries
1. **Broad to specific**: Start with broad industries, add specifics as needed
2. **Mirror categories**: Industry structure can mirror category structure
3. **Use for landing pages**: Each industry can have its own URL and page

### Tags
1. **Keep tags focused**: Each tag should represent one clear attribute
2. **Use colors wisely**: Group related tags by color
3. **Don't over-tag**: 3-5 tags per product is usually enough
4. **Reuse tags**: Create tags once, reuse across products
5. **Naming convention**: Use title case (e.g., "Eco-Friendly" not "eco-friendly")

---

## 📝 **Migration Notes**

- ✅ **Backward compatible**: Existing categories/industries continue to work (parent=None)
- ✅ **No data loss**: All existing data is preserved
- ✅ **Safe rollback**: Can be reverted if needed
- ✅ **Performance**: Indexes added for parent lookups
- ✅ **Deployed**: Changes pushed to Railway automatically

---

## 🎯 **Next Steps**

1. **Create Tags**: Add common tags (Eco-Friendly, Bestseller, etc.)
2. **Organize Categories**: Add parent-child relationships to existing categories
3. **Tag Products**: Apply relevant tags to all products
4. **Test Admin**: Try filtering, searching, and editing
5. **Plan Frontend**: Decide which features to expose to customers

---

## 📚 **Resources**

- **Shopify Tags Guide**: https://help.shopify.com/en/manual/shopify-admin/productivity-tools/using-tags
- **Django Tree Structures**: https://docs.djangoproject.com/en/5.0/ref/models/fields/#foreignkey
- **Admin Documentation**: http://127.0.0.1:8000/superusers/

---

**Questions?** Check the admin interface for inline help text on each field.
