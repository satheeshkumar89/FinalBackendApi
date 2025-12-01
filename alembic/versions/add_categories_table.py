"""Add categories table and migrate menu items

This migration:
1. Creates the categories table
2. Seeds it with 60 predefined categories
3. Adds category_id column to menu_items
4. Migrates existing category strings to category IDs
5. Drops the old category column

Revision ID: add_categories_table
Revises: 
Create Date: 2025-11-26
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'add_categories_table'
down_revision = None
branch_labels = None
depends_on = None


# Predefined categories
CATEGORIES = [
    {"id": 1, "name": "Beverages", "display_order": 1},
    {"id": 2, "name": "Breakfast", "display_order": 2},
    {"id": 3, "name": "Biryani", "display_order": 3},
    {"id": 4, "name": "Burgers", "display_order": 4},
    {"id": 5, "name": "Chinese", "display_order": 5},
    {"id": 6, "name": "North Indian", "display_order": 6},
    {"id": 7, "name": "South Indian", "display_order": 7},
    {"id": 8, "name": "Pizzas", "display_order": 8},
    {"id": 9, "name": "Desserts", "display_order": 9},
    {"id": 10, "name": "Salads", "display_order": 10},
    {"id": 11, "name": "Snacks", "display_order": 11},
    {"id": 12, "name": "Seafood", "display_order": 12},
    {"id": 13, "name": "BBQ & Grill", "display_order": 13},
    {"id": 14, "name": "Healthy Food", "display_order": 14},
    {"id": 15, "name": "Combos & Meals", "display_order": 15},
    {"id": 16, "name": "Pure Veg", "display_order": 16},
    {"id": 17, "name": "Ice Creams", "display_order": 17},
    {"id": 18, "name": "Indian Breads", "display_order": 18},
    {"id": 19, "name": "Thali", "display_order": 19},
    {"id": 20, "name": "Rice Bowls", "display_order": 20},
    {"id": 21, "name": "Pasta", "display_order": 21},
    {"id": 22, "name": "Sandwiches", "display_order": 22},
    {"id": 23, "name": "Wraps & Rolls", "display_order": 23},
    {"id": 24, "name": "Shawarma", "display_order": 24},
    {"id": 25, "name": "Momos", "display_order": 25},
    {"id": 26, "name": "Fried Rice & Noodles", "display_order": 26},
    {"id": 27, "name": "Chaat", "display_order": 27},
    {"id": 28, "name": "Sweets", "display_order": 28},
    {"id": 29, "name": "Bakery", "display_order": 29},
    {"id": 30, "name": "Tandoori", "display_order": 30},
    {"id": 31, "name": "Kebabs", "display_order": 31},
    {"id": 32, "name": "Gravy Dishes", "display_order": 32},
    {"id": 33, "name": "Soups", "display_order": 33},
    {"id": 34, "name": "Starters", "display_order": 34},
    {"id": 35, "name": "Curries", "display_order": 35},
    {"id": 36, "name": "Juices", "display_order": 36},
    {"id": 37, "name": "Shakes", "display_order": 37},
    {"id": 38, "name": "Tea & Coffee", "display_order": 38},
    {"id": 39, "name": "Appetizers", "display_order": 39},
    {"id": 40, "name": "Gujarati", "display_order": 40},
    {"id": 41, "name": "Rajasthani", "display_order": 41},
    {"id": 42, "name": "Andhra", "display_order": 42},
    {"id": 43, "name": "Hyderabadi", "display_order": 43},
    {"id": 44, "name": "Punjabi", "display_order": 44},
    {"id": 45, "name": "Mughlai", "display_order": 45},
    {"id": 46, "name": "Arabian", "display_order": 46},
    {"id": 47, "name": "Thai", "display_order": 47},
    {"id": 48, "name": "Japanese", "display_order": 48},
    {"id": 49, "name": "Korean", "display_order": 49},
    {"id": 50, "name": "Italian", "display_order": 50},
    {"id": 51, "name": "Mexican", "display_order": 51},
    {"id": 52, "name": "American", "display_order": 52},
    {"id": 53, "name": "Mediterranean", "display_order": 53},
    {"id": 54, "name": "Street Food", "display_order": 54},
    {"id": 55, "name": "Organic", "display_order": 55},
    {"id": 56, "name": "Vegan", "display_order": 56},
    {"id": 57, "name": "Jain Friendly", "display_order": 57},
    {"id": 58, "name": "Kids Menu", "display_order": 58},
    {"id": 59, "name": "Party Packs", "display_order": 59},
    {"id": 60, "name": "Weekend Specials", "display_order": 60}
]


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    # 1. Create categories table if it doesn't exist
    if not inspector.has_table('categories'):
        op.create_table(
            'categories',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('icon', sa.String(length=255), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
            sa.Column('display_order', sa.Integer(), nullable=True, default=0),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name')
        )
        op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)
        
        # 2. Seed categories only if we created the table
        categories_table = sa.table(
            'categories',
            sa.column('id', sa.Integer),
            sa.column('name', sa.String),
            sa.column('icon', sa.String),
            sa.column('is_active', sa.Boolean),
            sa.column('display_order', sa.Integer),
            sa.column('created_at', sa.DateTime)
        )
        
        op.bulk_insert(
            categories_table,
            [
                {
                    'id': cat['id'],
                    'name': cat['name'],
                    'icon': None,
                    'is_active': True,
                    'display_order': cat['display_order'],
                    'created_at': datetime.utcnow()
                }
                for cat in CATEGORIES
            ]
        )
    
    # 3. Add category_id column to menu_items if it doesn't exist
    menu_items_columns = [c['name'] for c in inspector.get_columns('menu_items')]
    if 'category_id' not in menu_items_columns:
        op.add_column('menu_items', sa.Column('category_id', sa.Integer(), nullable=True))
        op.create_foreign_key('fk_menu_items_category_id', 'menu_items', 'categories', ['category_id'], ['id'])
        
        # 4. Migrate existing category strings to category IDs (if needed)
        # This is a best-effort migration - matches category names case-insensitively
        connection = op.get_bind()
        
        # Create a mapping of category names to IDs
        category_map = {cat['name'].lower(): cat['id'] for cat in CATEGORIES}
        
        # Update menu_items with matching categories
        for cat_name, cat_id in category_map.items():
            connection.execute(
                sa.text(
                    "UPDATE menu_items SET category_id = :cat_id WHERE LOWER(category) = :cat_name"
                ),
                {"cat_id": cat_id, "cat_name": cat_name}
            )
        
        # 5. Drop the old category column
        if 'category' in menu_items_columns:
            op.drop_column('menu_items', 'category')


def downgrade():
    # 1. Add back the category string column
    op.add_column('menu_items', sa.Column('category', sa.String(length=100), nullable=True))
    
    # 2. Migrate category IDs back to strings
    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            UPDATE menu_items 
            SET category = (SELECT name FROM categories WHERE categories.id = menu_items.category_id)
            WHERE category_id IS NOT NULL
            """
        )
    )
    
    # 3. Drop category_id column and foreign key
    op.drop_constraint('fk_menu_items_category_id', 'menu_items', type_='foreignkey')
    op.drop_column('menu_items', 'category_id')
    
    # 4. Drop categories table
    op.drop_index(op.f('ix_categories_id'), table_name='categories')
    op.drop_table('categories')
