# utils/kpi_calculator.py
"""
KPI Calculator Utilities
All KPI calculation and ranking logic
"""

import numpy as np
import pandas as pd

class KPICalculator:
    """Calculate KPIs and rankings"""
    
    @staticmethod
    def safe_divide(numerator, denominator, default=0):
        """
        Safe division with error handling
        
        Args:
            numerator: Numerator value
            denominator: Denominator value
            default: Default value if division fails
            
        Returns:
            Result of division or default
        """
        try:
            if denominator == 0:
                return default
            return numerator / denominator
        except (TypeError, ValueError, ZeroDivisionError):
            return default
    
    @staticmethod
    def calculate_metrics(location_data):
        """
        Calculate all metrics for a location
        
        Args:
            location_data: Dictionary with location cost data
            
        Returns:
            Dictionary with calculated metrics
        """
        try:
            fuel_cost = KPICalculator.safe_divide(
                location_data['fuel_cons'] * location_data['diesel_price'],
                32
            )
            
            total_cost = (
                location_data['tls_opn'] +
                location_data['drivers_hauler'] +
                fuel_cost +
                location_data['ta_inc']
            )
            
            cost_per_lkg = KPICalculator.safe_divide(total_cost, location_data['lkgtc'])
            
            lkg_per_php = KPICalculator.safe_divide(
                location_data['lkgtc'],
                cost_per_lkg
            ) if cost_per_lkg > 0 else 0
            
            return {
                'fuel_cost': fuel_cost,
                'total_cost': total_cost,
                'cost_per_lkg': cost_per_lkg,
                'lkg_per_php': lkg_per_php
            }
        except Exception:
            return {
                'fuel_cost': 0,
                'total_cost': 0,
                'cost_per_lkg': 0,
                'lkg_per_php': 0
            }
    
    @staticmethod
    def normalize_cost_scores(costs):
        """
        Normalize cost scores (lower is better)
        
        Args:
            costs: List of cost values
            
        Returns:
            List of normalized scores (0-1)
        """
        if not costs:
            return []
        
        mx, mn = max(costs), min(costs)
        if mx == mn:
            return [0.5] * len(costs)
        
        return [(mx - c) / (mx - mn) for c in costs]
    
    @staticmethod
    def normalize_lkg_scores(lkgs):
        """
        Normalize LKG scores (higher is better)
        
        Args:
            lkgs: List of LKGTC values
            
        Returns:
            List of normalized scores (0-1)
        """
        if not lkgs:
            return []
        
        mx, mn = max(lkgs), min(lkgs)
        if mx == mn:
            return [0.5] * len(lkgs)
        
        return [(l - mn) / (mx - mn) for l in lkgs]
    
    @staticmethod
    def compute_kpis_adjustable(cost_scores, lkg_scores, cost_weight, lkg_weight):
        """
        Compute KPI scores with adjustable weights
        
        Args:
            cost_scores: List of normalized cost scores
            lkg_scores: List of normalized LKG scores
            cost_weight: Cost weight percentage (0-100)
            lkg_weight: LKG weight percentage (0-100)
            
        Returns:
            List of KPI scores
        """
        if len(cost_scores) != len(lkg_scores):
            return []
        
        # Convert to decimal
        cost_w = cost_weight / 100
        lkg_w = lkg_weight / 100
        
        return [cost_w * cs + lkg_w * ls for cs, ls in zip(cost_scores, lkg_scores)]
    
    @staticmethod
    def get_efficiency_class(kpi_score, all_scores):
        """
        Get efficiency class for a single score
        
        Args:
            kpi_score: KPI score value
            all_scores: List of all KPI scores for comparison
            
        Returns:
            Tuple of (css_class, rating, description)
        """
        try:
            if not all_scores or len(all_scores) < 2:
                return ('efficiency-average', '📊 Average', 'Not enough data')
            
            q75, q50, q25 = np.percentile(all_scores, [75, 50, 25])
            
            if kpi_score >= q75:
                return ('efficiency-excellent', '🥇 Excellent', f'Top 25% (Score: {kpi_score:.3f})')
            elif kpi_score >= q50:
                return ('efficiency-good', '🥈 Good', f'Above average (Score: {kpi_score:.3f})')
            elif kpi_score >= q25:
                return ('efficiency-average', '🥉 Average', f'Average (Score: {kpi_score:.3f})')
            else:
                return ('efficiency-poor', '❌ Poor', f'Below average (Score: {kpi_score:.3f})')
        except Exception:
            return ('efficiency-average', '📊 Average', 'Error')
    
    @staticmethod
    def get_efficiency_classes(scores):
        """
        Get efficiency classes for multiple scores
        
        Args:
            scores: List of KPI scores
            
        Returns:
            List of tuples (css_class, rating)
        """
        try:
            if not scores:
                return []
            
            q75, q50, q25 = np.percentile(scores, [75, 50, 25])
            classes = []
            
            for s in scores:
                if s >= q75:
                    classes.append(('efficiency-excellent', '🥇 Excellent'))
                elif s >= q50:
                    classes.append(('efficiency-good', '🥈 Good'))
                elif s >= q25:
                    classes.append(('efficiency-average', '🥉 Average'))
                else:
                    classes.append(('efficiency-poor', '❌ Poor'))
            
            return classes
        except Exception:
            return []
    
    @staticmethod
    def calculate_all_kpis(locations_data, cost_weight, lkg_weight):
        """
        Calculate KPIs for all locations
        
        Args:
            locations_data: Dictionary of all location data
            cost_weight: Cost weight percentage
            lkg_weight: LKG weight percentage
            
        Returns:
            Dictionary of {location: kpi_score}
        """
        try:
            data = []
            for loc, vals in locations_data.items():
                if vals['lkgtc'] > 0:
                    metrics = KPICalculator.calculate_metrics(vals)
                    data.append({
                        'location': loc,
                        'total_cost': metrics['total_cost'],
                        'lkgtc': vals['lkgtc']
                    })
            
            if len(data) < 2:
                return {}
            
            costs = [d['total_cost'] for d in data]
            lkgs = [d['lkgtc'] for d in data]
            
            cost_scores = KPICalculator.normalize_cost_scores(costs)
            lkg_scores = KPICalculator.normalize_lkg_scores(lkgs)
            kpis = KPICalculator.compute_kpis_adjustable(cost_scores, lkg_scores, cost_weight, lkg_weight)
            
            result = {}
            for i, d in enumerate(data):
                if i < len(kpis):
                    result[d['location']] = kpis[i]
            
            return result
        except Exception:
            return {}
    
    @staticmethod
    def rank_tls(data, cost_weight, lkg_weight):
        """
        Rank TLS locations
        
        Args:
            data: List of location data dictionaries
            cost_weight: Cost weight percentage
            lkg_weight: LKG weight percentage
            
        Returns:
            DataFrame with rankings
        """
        try:
            if not data:
                return pd.DataFrame()
            
            costs = [d.get('Total Cost', 0) for d in data]
            lkgs = [d.get('LKGTC', 0) for d in data]
            
            cost_scores = KPICalculator.normalize_cost_scores(costs)
            lkg_scores = KPICalculator.normalize_lkg_scores(lkgs)
            kpis = KPICalculator.compute_kpis_adjustable(cost_scores, lkg_scores, cost_weight, lkg_weight)
            
            # Add KPI scores to data
            for i, kpi in enumerate(kpis):
                if i < len(data):
                    data[i]['KPI Score'] = kpi
            
            df = pd.DataFrame(data)
            
            if 'KPI Score' in df.columns and not df['KPI Score'].empty:
                # Calculate rankings
                df['Overall Rank'] = df['KPI Score'].rank(method='dense', ascending=False).astype(int)
                df['Regional Rank'] = df.groupby('Region')['KPI Score'].rank(method='dense', ascending=False).astype(int)
                
                # Get efficiency classes
                df['Global Class'] = KPICalculator.get_efficiency_classes(df['KPI Score'].tolist())
                
                # Regional classes
                regional_classes = []
                for region, group in df.groupby('Region'):
                    region_classes = KPICalculator.get_efficiency_classes(group['KPI Score'].tolist())
                    regional_classes.extend(region_classes)
                df['Regional Class'] = regional_classes
            
            return df
        except Exception:
            return pd.DataFrame()
