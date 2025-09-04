#!/usr/bin/env python3
"""
Module de gouvernance éthique AI pour Baguette & Métro
Responsabilité, transparence, équité et sécurité des systèmes AI
"""

import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re

# Configuration du logging éthique
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EthicsLevel(Enum):
    """Niveaux de conformité éthique"""
    CRITICAL = "critical"      # Systèmes critiques (santé, transport)
    HIGH = "high"              # Systèmes importants (finance, éducation)
    MEDIUM = "medium"          # Systèmes standards (e-commerce, divertissement)
    LOW = "low"                # Systèmes basiques (utilitaires)

class BiasType(Enum):
    """Types de biais à détecter"""
    GENDER = "gender"
    RACE = "race"
    AGE = "age"
    RELIGION = "religion"
    POLITICAL = "political"
    ECONOMIC = "economic"
    GEOGRAPHIC = "geographic"
    CULTURAL = "cultural"

@dataclass
class EthicsAudit:
    """Audit éthique d'une interaction AI"""
    timestamp: str
    user_id: str
    session_id: str
    model_used: str
    prompt_hash: str
    response_hash: str
    bias_detected: List[str]
    toxicity_score: float
    fairness_score: float
    transparency_score: float
    compliance_score: float
    ethics_level: EthicsLevel
    flags: List[str]
    recommendations: List[str]

class AIEthicsGovernance:
    """Gouvernance éthique complète pour les systèmes AI"""
    
    def __init__(self):
        self.ethics_policies = self._load_ethics_policies()
        self.bias_patterns = self._load_bias_patterns()
        self.toxicity_indicators = self._load_toxicity_indicators()
        self.fairness_metrics = self._load_fairness_metrics()
        self.audit_log = []
        self.compliance_threshold = 0.8
        
    def _load_ethics_policies(self) -> Dict[str, Any]:
        """Chargement des politiques éthiques"""
        return {
            "core_principles": [
                "Respect de la dignité humaine",
                "Équité et non-discrimination",
                "Transparence et explicabilité",
                "Responsabilité et redevabilité",
                "Précaution et sécurité",
                "Inclusivité et accessibilité"
            ],
            "banned_content": [
                "Discours haineux",
                "Discrimination",
                "Violence",
                "Contenu illégal",
                "Manipulation politique",
                "Désinformation"
            ],
            "language_guidelines": {
                "fr": "Respecter la culture française et la diversité",
                "en": "Respect English culture and diversity",
                "jp": "日本の文化と多様性を尊重する"
            }
        }
    
    def _load_bias_patterns(self) -> Dict[BiasType, List[str]]:
        """Chargement des patterns de biais à détecter"""
        return {
            BiasType.GENDER: [
                r"\b(seulement|uniquement)\s+(les\s+)?(hommes|femmes)\b",
                r"\b(meilleur|pire)\s+(homme|femme)\b",
                r"\b(typiquement|naturellement)\s+(masculin|féminin)\b"
            ],
            BiasType.RACE: [
                r"\b(race|ethnie)\s+(supérieure|inférieure)\b",
                r"\bstéréotype\s+(racial|ethnique)\b",
                r"\b(profilage|discrimination)\s+(racial|ethnique)\b"
            ],
            BiasType.AGE: [
                r"\b(jeunes|vieux)\s+(incompétents|inutiles)\b",
                r"\b(âge)\s+(limite|restriction)\b",
                r"\b(génération)\s+(perdue|dépassée)\b"
            ],
            BiasType.RELIGION: [
                r"\b(religion)\s+(supérieure|inférieure)\b",
                r"\b(croyance)\s+(fausse|vraie)\b",
                r"\b(pratique)\s+(religieuse|spirituelle)\b"
            ],
            BiasType.POLITICAL: [
                r"\b(parti|idéologie)\s+(extrême|radical)\b",
                r"\b(opinion)\s+(politique)\s+(interdite)\b",
                r"\b(censure)\s+(politique)\b"
            ],
            BiasType.ECONOMIC: [
                r"\b(riche|pauvre)\s+(mérite|responsabilité)\b",
                r"\b(classe)\s+(sociale)\s+(déterminante)\b",
                r"\b(privilège)\s+(économique)\s+(justifié)\b"
            ],
            BiasType.GEOGRAPHIC: [
                r"\b(ville|région)\s+(dangereuse|sûre)\b",
                r"\b(quartier)\s+(problématique|privilégié)\b",
                r"\b(zone)\s+(à\s+éviter|recommandée)\b"
            ],
            BiasType.CULTURAL: [
                r"\b(culture)\s+(supérieure|inférieure)\b",
                r"\b(tradition)\s+(dépassée|moderne)\b",
                r"\b(coutume)\s+(étrange|normale)\b"
            ]
        }
    
    def _load_toxicity_indicators(self) -> List[str]:
        """Indicateurs de toxicité"""
        return [
            "agressif", "violent", "menaçant", "insultant",
            "humiliant", "dégradant", "manipulateur", "trompeur",
            "discriminatoire", "exclusif", "intolérant", "fanatique"
        ]
    
    def _load_fairness_metrics(self) -> Dict[str, Any]:
        """Métriques d'équité"""
        return {
            "representation": {
                "gender_balance": 0.5,
                "age_diversity": 0.7,
                "cultural_inclusion": 0.8
            },
            "accessibility": {
                "language_support": 0.9,
                "disability_support": 0.8,
                "digital_literacy": 0.7
            },
            "transparency": {
                "explainability": 0.8,
                "auditability": 0.9,
                "user_control": 0.7
            }
        }
    
    def analyze_prompt_ethics(self, prompt: str, language: str = "fr") -> Dict[str, Any]:
        """Analyse éthique d'un prompt utilisateur"""
        try:
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "prompt_hash": hashlib.sha256(prompt.encode()).hexdigest()[:16],
                "language": language,
                "bias_detected": [],
                "toxicity_score": 0.0,
                "fairness_score": 0.0,
                "compliance_score": 0.0,
                "flags": [],
                "recommendations": []
            }
            
            # Détection des biais
            for bias_type, patterns in self.bias_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, prompt, re.IGNORECASE):
                        analysis["bias_detected"].append(bias_type.value)
                        analysis["flags"].append(f"Biais {bias_type.value} détecté")
            
            # Score de toxicité
            toxicity_count = sum(1 for indicator in self.toxicity_indicators 
                               if indicator.lower() in prompt.lower())
            analysis["toxicity_score"] = min(toxicity_count / len(self.toxicity_indicators), 1.0)
            
            # Score d'équité
            bias_penalty = len(analysis["bias_detected"]) * 0.2
            toxicity_penalty = analysis["toxicity_score"] * 0.3
            analysis["fairness_score"] = max(0.0, 1.0 - bias_penalty - toxicity_penalty)
            
            # Score de conformité
            analysis["compliance_score"] = analysis["fairness_score"]
            
            # Recommandations
            if analysis["bias_detected"]:
                analysis["recommendations"].append(
                    "Reformuler le prompt pour éviter les biais détectés"
                )
            if analysis["toxicity_score"] > 0.5:
                analysis["recommendations"].append(
                    "Utiliser un langage plus respectueux et inclusif"
                )
            if analysis["compliance_score"] < self.compliance_threshold:
                analysis["flags"].append("NON CONFORME - Intervention requise")
                analysis["recommendations"].append(
                    "Demander à l'utilisateur de reformuler sa demande"
                )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erreur analyse éthique prompt: {e}")
            return {"error": str(e)}
    
    def analyze_response_ethics(self, response: str, prompt_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse éthique d'une réponse AI"""
        try:
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "response_hash": hashlib.sha256(response.encode()).hexdigest()[:16],
                "prompt_analysis": prompt_analysis,
                "response_bias": [],
                "response_toxicity": 0.0,
                "response_fairness": 0.0,
                "transparency_score": 0.0,
                "overall_compliance": 0.0,
                "flags": [],
                "recommendations": []
            }
            
            # Analyse de la réponse
            response_analysis = self.analyze_prompt_ethics(response)
            analysis["response_bias"] = response_analysis["bias_detected"]
            analysis["response_toxicity"] = response_analysis["toxicity_score"]
            analysis["response_fairness"] = response_analysis["fairness_score"]
            
            # Score de transparence
            transparency_indicators = [
                "je pense", "selon moi", "à mon avis",
                "je ne suis pas sûr", "je ne peux pas",
                "je ne sais pas", "je ne comprends pas"
            ]
            transparency_count = sum(1 for indicator in transparency_indicators 
                                   if indicator.lower() in response.lower())
            analysis["transparency_score"] = min(transparency_count / len(transparency_indicators), 1.0)
            
            # Conformité globale
            prompt_weight = 0.4
            response_weight = 0.4
            transparency_weight = 0.2
            
            analysis["overall_compliance"] = (
                prompt_analysis["compliance_score"] * prompt_weight +
                analysis["response_fairness"] * response_weight +
                analysis["transparency_score"] * transparency_weight
            )
            
            # Flags et recommandations
            if analysis["overall_compliance"] < self.compliance_threshold:
                analysis["flags"].append("RÉPONSE NON CONFORME")
                analysis["recommendations"].append(
                    "Revoir et corriger la réponse avant envoi"
                )
            
            if analysis["response_toxicity"] > 0.3:
                analysis["flags"].append("TOXICITÉ DÉTECTÉE")
                analysis["recommendations"].append(
                    "Filtrer la réponse pour éliminer le contenu toxique"
                )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erreur analyse éthique réponse: {e}")
            return {"error": str(e)}
    
    def create_ethical_prompt(self, base_prompt: str, language: str = "fr") -> str:
        """Création d'un prompt éthique et responsable"""
        try:
            ethical_guidelines = {
                "fr": """
                Instructions éthiques importantes :
                1. Respecter la dignité humaine et la diversité
                2. Éviter tout biais, discrimination ou stéréotype
                3. Fournir des informations factuelles et vérifiables
                4. Être inclusif et accessible à tous
                5. Respecter la culture et les valeurs locales
                6. Adopter un ton respectueux et bienveillant
                
                Prompt utilisateur : {prompt}
                
                Répondez de manière éthique, responsable et utile.
                """,
                "en": """
                Important ethical guidelines:
                1. Respect human dignity and diversity
                2. Avoid any bias, discrimination or stereotype
                3. Provide factual and verifiable information
                4. Be inclusive and accessible to all
                5. Respect local culture and values
                6. Adopt a respectful and caring tone
                
                User prompt: {prompt}
                
                Respond in an ethical, responsible and helpful manner.
                """,
                "jp": """
                重要な倫理ガイドライン：
                1. 人間の尊厳と多様性を尊重する
                2. 偏見、差別、ステレオタイプを避ける
                3. 事実に基づく検証可能な情報を提供する
                4. 包括的で誰でもアクセス可能にする
                5. 地域の文化と価値観を尊重する
                6. 敬意と配慮のある口調を採用する
                
                ユーザープロンプト：{prompt}
                
                倫理的、責任ある、有用な方法で回答してください。
                """
            }
            
            guideline = ethical_guidelines.get(language, ethical_guidelines["en"])
            return guideline.format(prompt=base_prompt)
            
        except Exception as e:
            logger.error(f"Erreur création prompt éthique: {e}")
            return base_prompt
    
    def audit_interaction(self, user_id: str, session_id: str, model_used: str,
                         prompt: str, response: str, language: str = "fr") -> EthicsAudit:
        """Audit éthique complet d'une interaction AI"""
        try:
            # Analyse du prompt
            prompt_analysis = self.analyze_prompt_ethics(prompt, language)
            
            # Analyse de la réponse
            response_analysis = self.analyze_response_ethics(response, prompt_analysis)
            
            # Détermination du niveau éthique
            if response_analysis["overall_compliance"] < 0.6:
                ethics_level = EthicsLevel.CRITICAL
            elif response_analysis["overall_compliance"] < 0.8:
                ethics_level = EthicsLevel.HIGH
            elif response_analysis["overall_compliance"] < 0.9:
                ethics_level = EthicsLevel.MEDIUM
            else:
                ethics_level = EthicsLevel.LOW
            
            # Création de l'audit
            audit = EthicsAudit(
                timestamp=datetime.now().isoformat(),
                user_id=user_id,
                session_id=session_id,
                model_used=model_used,
                prompt_hash=prompt_analysis["prompt_hash"],
                response_hash=response_analysis["response_hash"],
                bias_detected=prompt_analysis["bias_detected"] + response_analysis["response_bias"],
                toxicity_score=max(prompt_analysis["toxicity_score"], response_analysis["response_toxicity"]),
                fairness_score=min(prompt_analysis["fairness_score"], response_analysis["response_fairness"]),
                transparency_score=response_analysis["transparency_score"],
                compliance_score=response_analysis["overall_compliance"],
                ethics_level=ethics_level,
                flags=prompt_analysis["flags"] + response_analysis["flags"],
                recommendations=prompt_analysis["recommendations"] + response_analysis["recommendations"]
            )
            
            # Ajout au log d'audit
            self.audit_log.append(audit)
            
            # Log des incidents critiques
            if ethics_level == EthicsLevel.CRITICAL:
                logger.critical(f"INCIDENT ÉTHIQUE CRITIQUE - User: {user_id}, Session: {session_id}")
                logger.critical(f"Flags: {audit.flags}")
                logger.critical(f"Recommandations: {audit.recommendations}")
            
            return audit
            
        except Exception as e:
            logger.error(f"Erreur audit éthique: {e}")
            # Retour d'un audit d'erreur
            return EthicsAudit(
                timestamp=datetime.now().isoformat(),
                user_id=user_id,
                session_id=session_id,
                model_used=model_used,
                prompt_hash="",
                response_hash="",
                bias_detected=[],
                toxicity_score=1.0,
                fairness_score=0.0,
                transparency_score=0.0,
                compliance_score=0.0,
                ethics_level=EthicsLevel.CRITICAL,
                flags=["Erreur d'audit éthique"],
                recommendations=["Vérifier le système d'audit éthique"]
            )
    
    def get_ethics_report(self, days: int = 30) -> Dict[str, Any]:
        """Rapport éthique des interactions"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_audits = [
                audit for audit in self.audit_log
                if datetime.fromisoformat(audit.timestamp) > cutoff_date
            ]
            
            if not recent_audits:
                return {"message": "Aucun audit récent disponible"}
            
            # Statistiques
            total_interactions = len(recent_audits)
            critical_incidents = len([a for a in recent_audits if a.ethics_level == EthicsLevel.CRITICAL])
            high_risk = len([a for a in recent_audits if a.ethics_level == EthicsLevel.HIGH])
            
            # Biais les plus fréquents
            bias_counts = {}
            for audit in recent_audits:
                for bias in audit.bias_detected:
                    bias_counts[bias] = bias_counts.get(bias, 0) + 1
            
            # Scores moyens
            avg_toxicity = sum(a.toxicity_score for a in recent_audits) / total_interactions
            avg_fairness = sum(a.fairness_score for a in recent_audits) / total_interactions
            avg_compliance = sum(a.compliance_score for a in recent_audits) / total_interactions
            
            return {
                "period_days": days,
                "total_interactions": total_interactions,
                "critical_incidents": critical_incidents,
                "high_risk_interactions": high_risk,
                "risk_distribution": {
                    "critical": critical_incidents / total_interactions,
                    "high": high_risk / total_interactions,
                    "medium": len([a for a in recent_audits if a.ethics_level == EthicsLevel.MEDIUM]) / total_interactions,
                    "low": len([a for a in recent_audits if a.ethics_level == EthicsLevel.LOW]) / total_interactions
                },
                "bias_analysis": bias_counts,
                "average_scores": {
                    "toxicity": avg_toxicity,
                    "fairness": avg_fairness,
                    "compliance": avg_compliance
                },
                "compliance_status": "✅ CONFORME" if avg_compliance >= self.compliance_threshold else "❌ NON CONFORME",
                "recommendations": self._generate_ethics_recommendations(recent_audits)
            }
            
        except Exception as e:
            logger.error(f"Erreur rapport éthique: {e}")
            return {"error": str(e)}
    
    def _generate_ethics_recommendations(self, audits: List[EthicsAudit]) -> List[str]:
        """Génération de recommandations éthiques"""
        recommendations = []
        
        # Analyse des biais
        bias_counts = {}
        for audit in audits:
            for bias in audit.bias_detected:
                bias_counts[bias] = bias_counts.get(bias, 0) + 1
        
        if bias_counts:
            top_bias = max(bias_counts, key=bias_counts.get)
            recommendations.append(f"Former l'équipe sur la détection des biais {top_bias}")
        
        # Analyse de la toxicité
        high_toxicity = [a for a in audits if a.toxicity_score > 0.5]
        if high_toxicity:
            recommendations.append("Renforcer les filtres de contenu toxique")
        
        # Analyse de la conformité
        low_compliance = [a for a in audits if a.compliance_score < 0.7]
        if low_compliance:
            recommendations.append("Réviser les politiques éthiques et la formation")
        
        if not recommendations:
            recommendations.append("Continuer le monitoring éthique actuel")
        
        return recommendations

# Instance globale de gouvernance éthique
ai_ethics_governance = AIEthicsGovernance()

