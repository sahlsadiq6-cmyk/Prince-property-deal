"""
Property routes
Handles property listings, search, filtering
"""

from flask import Blueprint, request, jsonify
from models.models import db, Property, PropertyImage, PropertyStatus, Review, Inquiry, User
from utils.auth import token_required
from utils.database import track_event, paginate_query
from utils.security import sanitize_input, rate_limit
from datetime import datetime
import json

property_bp = Blueprint('properties', __name__, url_prefix='/api/properties')


@property_bp.route('/', methods=['GET'])
def get_properties():
    """Get all properties with filtering and pagination"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        city = request.args.get('city')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        property_type = request.args.get('type')
        bedrooms = request.args.get('bedrooms', type=int)
        status = request.args.get('status', 'available')
        
        # Build query
        query = Property.query.filter_by(status=PropertyStatus.AVAILABLE)
        
        if city:
            query = query.filter_by(city=sanitize_input(city))
        
        if min_price:
            query = query.filter(Property.price >= min_price)
        
        if max_price:
            query = query.filter(Property.price <= max_price)
        
        if property_type:
            query = query.filter_by(property_type=sanitize_input(property_type))
        
        if bedrooms:
            query = query.filter_by(bedrooms=bedrooms)
        
        # Pagination
        result = paginate_query(query, page, per_page)
        
        properties = [{
            'id': prop.id,
            'title': prop.title,
            'description': prop.description[:200],
            'price': prop.price,
            'property_type': prop.property_type,
            'bedrooms': prop.bedrooms,
            'bathrooms': prop.bathrooms,
            'square_feet': prop.square_feet,
            'address': prop.address,
            'city': prop.city,
            'main_image': prop.main_image,
            'views': prop.views
        } for prop in result['items']]
        
        # Track search event
        track_event('property_search', {
            'city': city,
            'price_range': f"{min_price}-{max_price}",
            'results': len(properties)
        })
        
        return jsonify({
            'data': properties,
            'pagination': {
                'current_page': result['current_page'],
                'per_page': result['per_page'],
                'total': result['total'],
                'pages': result['pages'],
                'has_next': result['has_next'],
                'has_prev': result['has_prev']
            }
        }), 200
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@property_bp.route('/<int:property_id>', methods=['GET'])
def get_property(property_id):
    """Get single property details"""
    try:
        property_obj = Property.query.get(property_id)
        
        if not property_obj:
            return jsonify({'message': 'Property not found'}), 404
        
        # Increment view count
        property_obj.views += 1
        db.session.commit()
        
        # Get images
        images = [img.image_url for img in property_obj.images.all()]
        
        # Get reviews
        reviews = []
        for review in property_obj.reviews.all():
            reviews.append({
                'id': review.id,
                'rating': review.rating,
                'comment': review.comment,
                'user': review.user.first_name,
                'created_at': review.created_at.isoformat()
            })
        
        property_data = {
            'id': property_obj.id,
            'title': property_obj.title,
            'description': property_obj.description,
            'price': property_obj.price,
            'property_type': property_obj.property_type,
            'bedrooms': property_obj.bedrooms,
            'bathrooms': property_obj.bathrooms,
            'square_feet': property_obj.square_feet,
            'address': property_obj.address,
            'city': property_obj.city,
            'state': property_obj.state,
            'zip_code': property_obj.zip_code,
            'year_built': property_obj.year_built,
            'condition': property_obj.condition,
            'features': property_obj.features,
            'main_image': property_obj.main_image,
            'images': images,
            'views': property_obj.views,
            'owner': {
                'id': property_obj.owner.id,
                'name': f"{property_obj.owner.first_name} {property_obj.owner.last_name}",
                'phone': property_obj.owner.phone,
                'email': property_obj.owner.email
            },
            'reviews': reviews,
            'average_rating': round(sum(r['rating'] for r in reviews) / len(reviews), 1) if reviews else 0,
            'created_at': property_obj.created_at.isoformat()
        }
        
        return jsonify({'data': property_data}), 200
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@property_bp.route('/', methods=['POST'])
@token_required
def create_property():
    """Create new property listing"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'price', 'address', 'city']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing required fields'}), 400
        
        property_obj = Property(
            title=sanitize_input(data['title']),
            description=sanitize_input(data.get('description', '')),
            price=float(data['price']),
            property_type=sanitize_input(data.get('property_type', '')),
            bedrooms=data.get('bedrooms', 0),
            bathrooms=data.get('bathrooms', 0),
            square_feet=data.get('square_feet', 0),
            address=sanitize_input(data['address']),
            city=sanitize_input(data['city']),
            state=sanitize_input(data.get('state', '')),
            zip_code=sanitize_input(data.get('zip_code', '')),
            year_built=data.get('year_built'),
            condition=sanitize_input(data.get('condition', '')),
            features=data.get('features', {}),
            owner_id=request.user_id,
            status=PropertyStatus.AVAILABLE
        )
        
        db.session.add(property_obj)
        db.session.flush()
        
        # Add images if provided
        if 'images' in data:
            for idx, image_url in enumerate(data['images']):
                img = PropertyImage(
                    property_id=property_obj.id,
                    image_url=image_url,
                    display_order=idx
                )
                db.session.add(img)
        
        db.session.commit()
        
        track_event('property_created', {'property_id': property_obj.id}, request.user_id)
        
        return jsonify({
            'message': 'Property created successfully',
            'property_id': property_obj.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


@property_bp.route('/<int:property_id>', methods=['PUT'])
@token_required
def update_property(property_id):
    """Update property"""
    try:
        property_obj = Property.query.get(property_id)
        
        if not property_obj:
            return jsonify({'message': 'Property not found'}), 404
        
        if property_obj.owner_id != request.user_id:
            return jsonify({'message': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            property_obj.title = sanitize_input(data['title'])
        if 'description' in data:
            property_obj.description = sanitize_input(data['description'])
        if 'price' in data:
            property_obj.price = float(data['price'])
        if 'bedrooms' in data:
            property_obj.bedrooms = data['bedrooms']
        if 'bathrooms' in data:
            property_obj.bathrooms = data['bathrooms']
        
        property_obj.updated_at = datetime.utcnow()
        db.session.commit()
        
        track_event('property_updated', {'property_id': property_id}, request.user_id)
        
        return jsonify({'message': 'Property updated successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


@property_bp.route('/<int:property_id>', methods=['DELETE'])
@token_required
def delete_property(property_id):
    """Delete property"""
    try:
        property_obj = Property.query.get(property_id)
        
        if not property_obj:
            return jsonify({'message': 'Property not found'}), 404
        
        if property_obj.owner_id != request.user_id:
            return jsonify({'message': 'Unauthorized'}), 403
        
        db.session.delete(property_obj)
        db.session.commit()
        
        track_event('property_deleted', {'property_id': property_id}, request.user_id)
        
        return jsonify({'message': 'Property deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


@property_bp.route('/<int:property_id>/inquire', methods=['POST'])
@rate_limit("5 per hour")
def create_inquiry(property_id):
    """Create property inquiry"""
    try:
        property_obj = Property.query.get(property_id)
        
        if not property_obj:
            return jsonify({'message': 'Property not found'}), 404
        
        data = request.get_json()
        
        inquiry = Inquiry(
            property_id=property_id,
            name=sanitize_input(data.get('name', '')),
            email=sanitize_input(data.get('email', '')),
            phone=sanitize_input(data.get('phone', '')),
            message=sanitize_input(data.get('message', ''))
        )
        
        db.session.add(inquiry)
        db.session.commit()
        
        track_event('property_inquiry', {'property_id': property_id})
        
        return jsonify({
            'message': 'Inquiry submitted successfully',
            'inquiry_id': inquiry.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


@property_bp.route('/<int:property_id>/review', methods=['POST'])
@token_required
@rate_limit("10 per day")
def add_review(property_id):
    """Add review to property"""
    try:
        property_obj = Property.query.get(property_id)
        
        if not property_obj:
            return jsonify({'message': 'Property not found'}), 404
        
        data = request.get_json()
        
        if 'rating' not in data or not (1 <= data['rating'] <= 5):
            return jsonify({'message': 'Rating must be between 1 and 5'}), 400
        
        review = Review(
            property_id=property_id,
            user_id=request.user_id,
            rating=data['rating'],
            comment=sanitize_input(data.get('comment', ''))
        )
        
        db.session.add(review)
        db.session.commit()
        
        return jsonify({
            'message': 'Review added successfully',
            'review_id': review.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500
