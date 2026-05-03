from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Opportunity

opp_bp = Blueprint('opportunities', __name__)

@opp_bp.route('/api/opportunities', methods=['GET', 'POST'])
@login_required
def handle_opportunities():
    if request.method == 'GET':
        opportunities = Opportunity.query.filter_by(admin_id=current_user.id).all()
        output = []
        for opp in opportunities:
            output.append({
                "id": opp.id,
                "name": opp.name,
                "category": opp.category,
                "duration": opp.duration,
                "start_date": opp.start_date,
                "description": opp.description,
                "skills": opp.skills,
                "future_opportunities": opp.future_opportunities,
                "max_applicants": opp.max_applicants
            })
        return jsonify(output), 200

    elif request.method == 'POST':
        data = request.get_json()
        required = ["name", "duration", "start_date", "description", "skills", "category", "future_opportunities"]
        
        if not data or not all(k in data and data[k] for k in required):
            return jsonify({"error": "All required fields must be filled"}), 400

        new_opp = Opportunity(
            admin_id=current_user.id,
            name=data['name'],
            duration=data['duration'],
            start_date=data['start_date'],
            description=data['description'],
            skills=data['skills'],
            category=data['category'],
            future_opportunities=data['future_opportunities'],
            max_applicants=data.get('max_applicants')
        )
        db.session.add(new_opp)
        db.session.commit()
        return jsonify({"message": "Opportunity added successfully", "id": new_opp.id}), 201

@opp_bp.route('/api/opportunities/<int:opp_id>', methods=['PUT', 'DELETE'])
@login_required
def handle_single_opportunity(opp_id):
    opp = Opportunity.query.get_or_404(opp_id)
    
    if opp.admin_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    if request.method == 'PUT':
        data = request.get_json()
        opp.name = data.get('name', opp.name)
        opp.duration = data.get('duration', opp.duration)
        opp.start_date = data.get('start_date', opp.start_date)
        opp.description = data.get('description', opp.description)
        opp.skills = data.get('skills', opp.skills)
        opp.category = data.get('category', opp.category)
        opp.future_opportunities = data.get('future_opportunities', opp.future_opportunities)
        opp.max_applicants = data.get('max_applicants', opp.max_applicants)
        
        db.session.commit()
        return jsonify({"message": "Opportunity updated successfully"}), 200

    elif request.method == 'DELETE':
        db.session.delete(opp)
        db.session.commit()
        return jsonify({"message": "Opportunity deleted successfully"}), 200