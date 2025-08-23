
class EmergencySystem:
    """
    Complete emergency response system for blood donation
    Handles SMS/WhatsApp alerts and donor ranking
    """

    def __init__(self, ranking_system):
        self.ranking_system = ranking_system

    def process_emergency_request(self, message):
        """
        Process emergency SMS: "HELP O+ 560001"
        Returns ranked donor list and alert messages
        """
        try:
            parts = message.strip().upper().split()
            if len(parts) >= 2 and parts[0] == "HELP":
                blood_group = parts[1]
                pincode = parts[2] if len(parts) > 2 else "500001"  # Default Hyderabad

                # Convert pincode to rough coordinates (simplified)
                lat, lon = self.pincode_to_coordinates(pincode)

                emergency_request = {
                    'blood_group': blood_group,
                    'latitude': lat,
                    'longitude': lon,
                    'urgency': 'high',
                    'quantity': '1 unit'
                }

                # Get ranked donors
                donors = self.ranking_system.get_compatible_donors(blood_group)

                # Create alert messages
                alerts = []
                for i, (_, donor) in enumerate(donors.head(10).iterrows()):
                    message = f"🚨 URGENT: {blood_group} blood needed near {pincode}. Can you help? Reply YES/NO"
                    alerts.append({
                        'donor_id': donor['user_id'],
                        'message': message,
                        'priority': i + 1
                    })

                return {
                    'status': 'success',
                    'compatible_donors': len(donors),
                    'alerts_sent': len(alerts),
                    'top_donors': alerts
                }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def pincode_to_coordinates(self, pincode):
        """Convert pincode to approximate coordinates"""
        # Simplified mapping - in production, use a proper geocoding API
        pincode_map = {
            '500001': (17.3850, 78.4867),  # Hyderabad
            '560001': (12.9716, 77.5946),  # Bangalore
            '400001': (19.0760, 72.8777),  # Mumbai
            '110001': (28.6139, 77.2090),  # Delhi
        }
        return pincode_map.get(pincode, (17.3850, 78.4867))  # Default to Hyderabad
