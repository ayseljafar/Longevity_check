from typing import List, Dict, Any
import os
import json

class KnowledgeBase:
    """
    Manages the knowledge base for supplements, protocols, and medical disclaimers.
    For V0, this uses a simple JSON file-based approach.
    """
    
    def __init__(self, data_file: str = None):
        """
        Initialize the knowledge base.
        
        Parameters:
        - data_file: Path to JSON file containing supplement data (optional)
        """
        # Default knowledge base if no file is provided
        self.supplements = self._load_default_supplements()
        
        # Load from file if provided
        if data_file and os.path.exists(data_file):
            try:
                with open(data_file, 'r') as f:
                    data = json.load(f)
                    if 'supplements' in data and isinstance(data['supplements'], list):
                        self.supplements = data['supplements']
            except Exception as e:
                print(f"Error loading knowledge base from file: {str(e)}")
    
    def get_supplements_for_goal(self, goal: str) -> List[Dict[str, Any]]:
        """
        Retrieve supplements relevant to a specific health goal.
        
        Parameters:
        - goal: The health goal to find supplements for
        
        Returns:
        - List of supplement dictionaries
        """
        goal = goal.lower().strip()
        relevant_supplements = []
        
        for supplement in self.supplements:
            # Check if the goal is in the supplement's relevant_goals list
            if 'relevant_goals' in supplement and any(
                goal in target_goal.lower() for target_goal in supplement['relevant_goals']
            ):
                relevant_supplements.append(supplement)
                
            # Also check the description for relevant keywords
            elif 'description' in supplement and goal in supplement['description'].lower():
                relevant_supplements.append(supplement)
        
        return relevant_supplements
    
    def get_all_supplements(self) -> List[Dict[str, Any]]:
        """
        Retrieve all supplements in the knowledge base.
        
        Returns:
        - List of all supplement dictionaries
        """
        return self.supplements
    
    def get_disclaimer(self, disclaimer_type: str = "general") -> str:
        """
        Get a specific type of medical disclaimer.
        
        Parameters:
        - disclaimer_type: Type of disclaimer (general, supplements, etc.)
        
        Returns:
        - Disclaimer text
        """
        disclaimers = {
            "general": """
                DISCLAIMER: This information is for educational purposes only and is not intended 
                as medical advice, diagnosis, or treatment. Always consult with a qualified 
                healthcare provider before making any changes to your health regimen.
            """,
            
            "supplements": """
                SUPPLEMENT DISCLAIMER: Dietary supplements are not regulated by the FDA and 
                have not been evaluated to treat, cure, or prevent any disease. Results may 
                vary. Consult with a healthcare professional before starting any supplement.
            """,
            
            "prescriptions": """
                PRESCRIPTION DISCLAIMER: Prescription medications require evaluation by a 
                licensed healthcare provider. This information does not constitute medical 
                advice and does not replace consultation with a healthcare professional.
            """
        }
        
        return disclaimers.get(disclaimer_type, disclaimers["general"]).strip()
    
    def _load_default_supplements(self) -> List[Dict[str, Any]]:
        """
        Load the default supplement knowledge base.
        
        Returns:
        - List of supplement dictionaries
        """
        return [
            {
                "name": "Vitamin D3",
                "description": "Vital for immune function, bone health, and overall longevity. Many people are deficient, especially in northern climates or those with limited sun exposure.",
                "dosage": "1,000-5,000 IU daily, ideally with K2 for better calcium absorption",
                "cautions": "High doses may cause hypercalcemia. Blood levels should be monitored with dosages above 5,000 IU daily.",
                "evidence_level": "Strong - multiple randomized controlled trials",
                "relevant_goals": ["immune support", "bone health", "longevity", "general health"],
                "referral_link": "https://www.amazon.com/Nature-Made-Vitamin-Softgels-Count/dp/B08MQ5H83P/ref=sr_1_1?keywords=vitamin+d3+5000+iu+nature+made&qid=1711440000&sr=8-1"
            },
            {
                "name": "Magnesium",
                "description": "Essential mineral involved in over 300 enzymatic reactions. Supports muscle function, sleep quality, stress response, and cardiovascular health.",
                "dosage": "200-400mg daily, preferably magnesium glycinate or threonate forms for better absorption",
                "cautions": "May cause loose stools at higher doses. Not recommended for those with kidney disease without medical supervision.",
                "evidence_level": "Strong - multiple clinical trials",
                "relevant_goals": ["sleep improvement", "stress reduction", "muscle recovery", "heart health"],
                "referral_link": "https://www.amazon.com/Nature-Made-Magnesium-Supplement-Count/dp/B07RM7VXFV/ref=sr_1_1?keywords=magnesium+glycinate+nature+made&qid=1711440000&sr=8-1"
            },
            {
                "name": "Omega-3 Fatty Acids",
                "description": "Essential fatty acids that reduce inflammation, support brain health, and improve cardiovascular markers. DHA and EPA are the most studied beneficial forms.",
                "dosage": "1-3g combined EPA+DHA daily",
                "cautions": "May have blood-thinning effects. Discontinue 1-2 weeks before surgery. Choose low-mercury products.",
                "evidence_level": "Strong - extensive research including large-scale trials",
                "relevant_goals": ["heart health", "brain function", "inflammation reduction", "joint pain"],
                "referral_link": "https://www.amazon.com/Nordic-Naturals-Ultimate-Omega-Softgels/dp/B01MULTGUM/ref=sr_1_1?keywords=nordic+naturals+ultimate+omega&qid=1711440000&sr=8-1"
            },
            {
                "name": "Berberine",
                "description": "Plant compound that helps regulate blood glucose, improves lipid profiles, and supports gut health. Often compared to metformin for its metabolic benefits.",
                "dosage": "500mg 1-3 times daily with meals",
                "cautions": "May cause digestive discomfort. Can interact with certain medications including antibiotics and blood thinners.",
                "evidence_level": "Moderate to strong - multiple clinical trials",
                "relevant_goals": ["blood sugar control", "weight loss", "metabolic health", "longevity"],
                "referral_link": "https://www.amazon.com/Thorne-Research-Berberine-Supplement-Capsules/dp/B09BYRGXHL/ref=sr_1_1?keywords=thorne+berberine&qid=1711440000&sr=8-1"
            },
            {
                "name": "CoQ10 (Ubiquinol)",
                "description": "Antioxidant important for cellular energy production in the mitochondria. Levels decline with age and statin use. Supports heart health and energy levels.",
                "dosage": "100-200mg daily with a fatty meal for better absorption",
                "cautions": "Generally well-tolerated. May interact with blood thinners and blood pressure medications.",
                "evidence_level": "Moderate - multiple clinical trials",
                "relevant_goals": ["energy", "heart health", "statin side effect reduction", "anti-aging"],
                "referral_link": "https://www.amazon.com/NOW-Supplements-Ubiquinol-CoQ10-Softgels/dp/B0014AU4PY/ref=sr_1_1?keywords=now+ubiquinol+coq10&qid=1711440000&sr=8-1"
            },
            {
                "name": "NMN (Nicotinamide Mononucleotide)",
                "description": "Precursor to NAD+, which declines with age and is crucial for cellular energy production and DNA repair. May support healthy aging and metabolic function.",
                "dosage": "250-1,000mg daily",
                "cautions": "Relatively new supplement with limited long-term human studies. Generally considered safe but expensive.",
                "evidence_level": "Emerging - animal studies promising, human studies limited",
                "relevant_goals": ["longevity", "anti-aging", "energy", "cellular health"],
                "referral_link": "https://www.amazon.com/ProHealth-Longevity-Nicotinamide-Mononucleotide-Supplement/dp/B07PVPLJ8P/ref=sr_1_1?keywords=prohealth+longevity+nmn&qid=1711440000&sr=8-1"
            },
            {
                "name": "Ashwagandha",
                "description": "Adaptogenic herb that helps the body manage stress. May reduce cortisol levels, improve sleep quality, and support thyroid function.",
                "dosage": "300-600mg daily of root extract standardized to 5% withanolides",
                "cautions": "May increase thyroid hormone levels. Not recommended for pregnant women or those with autoimmune thyroid conditions.",
                "evidence_level": "Moderate - several clinical trials",
                "relevant_goals": ["stress reduction", "sleep", "anxiety", "thyroid support"],
                "referral_link": "https://www.amazon.com/NOW-Supplements-Ashwagandha-450mg-Capsules/dp/B06X9T1Y8F/ref=sr_1_1?keywords=now+ashwagandha+450mg&qid=1711440000&sr=8-1"
            },
            {
                "name": "Creatine Monohydrate",
                "description": "One of the most well-researched supplements, supports muscle energy, cognitive function, and overall cellular energy production.",
                "dosage": "3-5g daily, no loading phase necessary for general health",
                "cautions": "May cause water retention initially. Stay well hydrated when supplementing.",
                "evidence_level": "Strong - extensive research and clinical trials",
                "relevant_goals": ["muscle strength", "cognitive performance", "energy", "exercise performance"],
                "referral_link": "https://www.amazon.com/ON-Optimum-Nutrition-Creatine-Powder/dp/B002DYIZEO/ref=sr_1_1?keywords=optimum+nutrition+creatine+monohydrate&qid=1711440000&sr=8-1"
            },
            {
                "name": "Zinc",
                "description": "Essential mineral critical for immune function, testosterone production, and enzyme reactions. Many are deficient due to soil depletion and dietary choices.",
                "dosage": "15-30mg daily, preferably with copper to prevent imbalance",
                "cautions": "High doses may deplete copper. Long-term high-dose supplementation not recommended without monitoring.",
                "evidence_level": "Strong - well-established essential nutrient",
                "relevant_goals": ["immune support", "hormone balance", "skin health", "wound healing"],
                "referral_link": "https://www.amazon.com/Nature-Made-Zinc-Supplement-Count/dp/B0912CSGB6/ref=sr_1_1?keywords=nature+made+zinc+30mg&qid=1711440000&sr=8-1"
            },
            {
                "name": "Lion's Mane Mushroom",
                "description": "Medicinal mushroom that supports nerve growth factor (NGF) production. May enhance cognitive function, memory, and nervous system health.",
                "dosage": "500-1,000mg daily of extract standardized for beta-glucans",
                "cautions": "May cause digestive upset in some individuals. Those with mushroom allergies should avoid.",
                "evidence_level": "Moderate - promising research but limited large-scale human trials",
                "relevant_goals": ["cognitive enhancement", "brain health", "memory", "focus"],
                "referral_link": "https://www.amazon.com/dp/B078SZX3ML?tag=longevityagent-20"
            }
        ]
