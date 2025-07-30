#!/usr/bin/env python3
"""
SQLAlchemy Learning File - All Main Concepts
Run each cell to learn SQLAlchemy step by step.

This file demonstrates:
- Database engine setup and configuration
- Model definitions with relationships
- CRUD operations (Create, Read, Update, Delete)
- Advanced queries with filtering, joins, and aggregation
- Transactions and error handling
- Bulk operations for performance
- Database metadata inspection
"""

#%%
# Core SQLAlchemy imports for database operations
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base  # For creating model base class
from sqlalchemy.orm import sessionmaker, relationship    # For sessions and relationships
from sqlalchemy.sql import func                         # For SQL functions like COUNT, SUM
from datetime import datetime, timezone
import os

# Create database engine - this is the connection to your database
# sqlite:///learning.db - creates a SQLite database file named 'learning.db'
# echo=True - shows all SQL queries in console (great for learning!)
engine = create_engine("sqlite:///learning.db", echo=True)

# Create session factory - this creates database sessions
# autocommit=False - changes aren't saved until you call commit()
# autoflush=False - changes aren't sent to database until you call flush()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base - all models will inherit from this
# This is the foundation for defining database tables as Python classes
Base = declarative_base()

print("✅ Engine and session created")
print("✅ Base class for models created")

#%%
# Cell 2: Define Models (Tables)
print("=== Cell 2: Define Models ===")

class User(Base):
    """
    User model - represents the 'users' table in the database.
    
    This demonstrates:
    - Primary keys (id)
    - Indexed columns for faster queries
    - Unique constraints
    - Default values
    - Relationships to other tables
    """
    __tablename__ = "users"  # The actual table name in the database
    
    # Primary key - auto-incrementing integer
    id = Column(Integer, primary_key=True, index=True)
    
    # String columns with constraints
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    
    # Boolean column with default value
    is_active = Column(Boolean, default=True)
    
    # DateTime column with default value (current timestamp)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    # Relationship - one user can have many posts
    # back_populates creates bidirectional relationship
    posts = relationship("Post", back_populates="author")

class Post(Base):
    """
    Post model - represents the 'posts' table in the database.
    
    This demonstrates:
    - Foreign keys (links to users table)
    - Text columns for long content
    - Relationships back to parent table
    """
    __tablename__ = "posts"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # String and text columns
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=True)  # Text can store longer content than String
    
    # Boolean with default
    published = Column(Boolean, default=False)
    
    # DateTime with default
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign key - creates a link to the users table
    # This creates a column called 'author_id' that references users.id
    author_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationship - each post belongs to one user
    # This allows you to access post.author to get the user who wrote it
    author = relationship("User", back_populates="posts")

print("✅ User and Post models defined")
print("✅ Relationships established (User -> Posts)")

#%%
# Cell 3: Create Tables
print("=== Cell 3: Create Tables ===")

# Create all tables defined in models
# This generates the actual SQL CREATE TABLE statements
# and executes them against the database
Base.metadata.create_all(bind=engine)
print("✅ All tables created in database")

#%%
# Cell 4: Basic CRUD Operations - CREATE
print("=== Cell 4: CREATE Operations ===")

# Get a database session - this is like opening a connection
# All database operations happen within a session
db = SessionLocal()

# Method 1: Create object from dictionary
user_data = {
    "username": "john_doe",
    "email": "john@example.com",
    "is_active": True
}

# Create User object from dictionary using ** unpacking
new_user = User(**user_data)

# Add to session - this stages the object for insertion
db.add(new_user)

# Commit to database - this actually saves the data
db.commit()

# Refresh object - this loads the auto-generated ID and other defaults
db.refresh(new_user)

print(f"✅ Created user: {new_user.username} (ID: {new_user.id})")

# Method 2: Create object directly
post_data = {
    "title": "My First Post",
    "content": "This is the content of my first post!",
    "published": True,
    "author_id": new_user.id  # Link to the user we just created
}

new_post = Post(**post_data)
db.add(new_post)
db.commit()
db.refresh(new_post)

print(f"✅ Created post: {new_post.title} (ID: {new_post.id})")

#%%
# Cell 5: Basic CRUD Operations - READ
print("=== Cell 5: READ Operations ===")

# Method 1: Get by primary key (ID)
user = db.query(User).filter(User.id == 1).first()
print(f"✅ Found user by ID: {user.username}")
#%%

# Method 2: Get by unique field
user = db.query(User).filter(User.username == "john_doe").first()
print(f"✅ Found user by username: {user.username}")

# Method 3: Get all records
all_users = db.query(User).all()
print(f"✅ All users: {len(all_users)} found")

# Method 4: Get all posts
all_posts = db.query(Post).all()
print(f"✅ All posts: {len(all_posts)} found")

# Method 5: Use relationships to get related data
# This uses the relationship we defined in the User model
user_posts = user.posts
print(f"✅ Posts by {user.username}: {len(user_posts)} found")

#%%
# Cell 6: Basic CRUD Operations - UPDATE
print("=== Cell 6: UPDATE Operations ===")

# Method 1: Update by modifying object attributes
user.username = "john_updated"
db.commit()  # Save changes to database
print(f"✅ Updated username to: {user.username}")

# Method 2: Update post
post = db.query(Post).filter(Post.id == 1).first()
post.title = "Updated Post Title"
db.commit()
print(f"✅ Updated post title to: {post.title}")

#%%
# Cell 7: Basic CRUD Operations - DELETE
print("=== Cell 7: DELETE Operations ===")

# Method 1: Delete by finding object first
post_to_delete = db.query(Post).filter(Post.id == 1).first()
if post_to_delete:
    db.delete(post_to_delete)  # Mark for deletion
    db.commit()                # Actually delete from database
    print("✅ Post deleted")

# Method 2: Verify deletion
deleted_post = db.query(Post).filter(Post.id == 1).first()
if deleted_post is None:
    print("✅ Post successfully deleted (not found)")

#%%
# Cell 8: Advanced Queries - Filtering
print("=== Cell 8: Advanced Queries - Filtering ===")

# Create more test data for demonstration
test_users = [
    {"username": "alice", "email": "alice@example.com"},
    {"username": "bob", "email": "bob@example.com"},
    {"username": "charlie", "email": "charlie@example.com"}
]

# Bulk insert using loop
for user_data in test_users:
    user = User(**user_data)
    db.add(user)
db.commit()

# Filter 1: Simple equality filter
active_users = db.query(User).filter(User.is_active == True).all()
print(f"✅ Active users: {len(active_users)}")

# Filter 2: String contains (LIKE query)
gmail_users = db.query(User).filter(User.email.contains("@gmail")).all()
print(f"✅ Gmail users: {len(gmail_users)}")

# Filter 3: Boolean filter
published_posts = db.query(Post).filter(Post.published == True).all()
print(f"✅ Published posts: {len(published_posts)}")

#%%
# Cell 9: Advanced Queries - Ordering and Limiting
print("=== Cell 9: Advanced Queries - Ordering and Limiting ===")

# Order by ascending (alphabetical)
users_ordered = db.query(User).order_by(User.username).all()
print("✅ Users ordered by username:")
for user in users_ordered:
    print(f"  - {user.username}")

# Order by descending (newest first) and limit results
latest_posts = db.query(Post).order_by(Post.created_at.desc()).limit(5).all()
print(f"✅ Latest 5 posts: {len(latest_posts)}")

#%%
# Cell 10: Advanced Queries - Joins and Relationships
print("=== Cell 10: Advanced Queries - Joins and Relationships ===")

# Method 1: Explicit JOIN - get posts with their authors
# This creates a SQL JOIN between posts and users tables
posts_with_authors = db.query(Post, User).join(User).all()
print("✅ Posts with authors:")
for post, author in posts_with_authors:
    print(f"  - {post.title} by {author.username}")

# Method 2: Using relationships - get user with all their posts
# This uses the relationship we defined, no explicit JOIN needed
user_with_posts = db.query(User).filter(User.username == "john_updated").first()
if user_with_posts:
    print(f"✅ User {user_with_posts.username} has {len(user_with_posts.posts)} posts")

#%%
# Cell 11: Advanced Queries - Aggregation
print("=== Cell 11: Advanced Queries - Aggregation ===")

from sqlalchemy import func

# Count total users using SQL COUNT function
total_users = db.query(func.count(User.id)).scalar()
print(f"✅ Total users: {total_users}")

# Count posts per user using GROUP BY
# This creates a SQL query like: SELECT username, COUNT(posts.id) FROM users JOIN posts GROUP BY username
posts_per_user = db.query(User.username, func.count(Post.id)).join(Post).group_by(User.username).all()
print("✅ Posts per user:")
for username, count in posts_per_user:
    print(f"  - {username}: {count} posts")

#%%
# Cell 12: Advanced Queries - Complex Filtering
print("=== Cell 12: Advanced Queries - Complex Filtering ===")

from sqlalchemy import and_, or_, not_

# Complex filter with AND conditions
# Find users who are active AND have gmail addresses
active_gmail_users = db.query(User).filter(
    and_(
        User.is_active == True,
        User.email.contains("@gmail")
    )
).all()
print(f"✅ Active Gmail users: {len(active_gmail_users)}")

# Complex filter with OR conditions
# Find posts that are published OR created after 2024
published_or_recent = db.query(Post).filter(
    or_(
        Post.published == True,
        Post.created_at >= datetime(2024, 1, 1)
    )
).all()
print(f"✅ Published or recent posts: {len(published_or_recent)}")

#%%
# Cell 13: Transactions and Error Handling
print("=== Cell 13: Transactions and Error Handling ===")

# Start a transaction - all operations will be atomic
# Either all succeed or all fail (rollback)
try:
    # Create a user
    new_user = User(username="transaction_test", email="test@example.com")
    db.add(new_user)
    
    # Create a post for this user
    new_post = Post(title="Transaction Test Post", author_id=new_user.id)
    db.add(new_post)
    
    # Commit the transaction - save everything to database
    db.commit()
    print("✅ Transaction completed successfully")
    
except Exception as e:
    # Rollback on error - undo all changes in this transaction
    db.rollback()
    print(f"❌ Transaction failed: {e}")

#%%
# Cell 14: Bulk Operations
print("=== Cell 14: Bulk Operations ===")

# Bulk insert - much faster than individual inserts
bulk_users = [
    User(username="user1", email="user1@example.com"),
    User(username="user2", email="user2@example.com"),
    User(username="user3", email="user3@example.com")
]

# Add all objects at once
db.bulk_save_objects(bulk_users)
db.commit()
print("✅ Bulk inserted 3 users")

# Bulk update - update multiple records with one query
# This is much more efficient than updating one by one
db.query(User).filter(User.username.like("user%")).update({"is_active": False})
db.commit()
print("✅ Bulk updated users with 'user' prefix to inactive")

#%%
# Cell 15: Database Information and Metadata
print("=== Cell 15: Database Information ===")

from sqlalchemy import inspect

# Create inspector to examine database structure
inspector = inspect(engine)

# Get all table names in the database
tables = inspector.get_table_names()
print(f"✅ Tables in database: {tables}")

# Get detailed column information for a specific table
columns = inspector.get_columns("users")
print("✅ Columns in users table:")
for column in columns:
    print(f"  - {column['name']}: {column['type']}")

#%%
# Cell 16: Cleanup and Summary
print("=== Cell 16: Cleanup and Summary ===")

# Get final statistics using aggregation
total_users = db.query(func.count(User.id)).scalar()
total_posts = db.query(func.count(Post.id)).scalar()

print("📊 Final Database Statistics:")
print(f"  - Total users: {total_users}")
print(f"  - Total posts: {total_posts}")

# Always close the session when done
# This releases database connections back to the pool
db.close()
print("✅ Database session closed")

print("\n🎉 SQLAlchemy Learning Complete!")
print("You've learned:")
print("  ✅ Basic CRUD operations")
print("  ✅ Relationships and joins")
print("  ✅ Advanced queries and filtering")
print("  ✅ Transactions and error handling")
print("  ✅ Bulk operations")
print("  ✅ Database metadata") 