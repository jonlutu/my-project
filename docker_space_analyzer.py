#!/usr/bin/env python3
"""
Docker Space Analyzer & Optimizer
Analyzes Jonathan's Docker space usage (45.7GB concern) and provides intelligent cleanup recommendations.
Perfect for ComfyUI, development containers, and space optimization.
"""

import subprocess
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class DockerSpaceAnalyzer:
    def __init__(self):
        self.analysis_file = Path("docker_space_analysis.json")
        
    def get_docker_system_info(self) -> Dict:
        """Get comprehensive Docker system information."""
        try:
            result = subprocess.run(['docker', 'system', 'df', '--format', 'json'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {}
        except:
            return {}
    
    def get_detailed_images(self) -> List[Dict]:
        """Get detailed information about all Docker images."""
        images = []
        try:
            result = subprocess.run(['docker', 'images', '--format', 
                                   '{{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}\t{{.ID}}'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('\t')
                        if len(parts) >= 5:
                            size_str = parts[2]
                            size_bytes = self._parse_size_to_bytes(size_str)
                            
                            images.append({
                                'repository': parts[0],
                                'tag': parts[1], 
                                'size_str': size_str,
                                'size_bytes': size_bytes,
                                'created': parts[3],
                                'id': parts[4],
                                'full_name': f"{parts[0]}:{parts[1]}" if parts[1] != '<none>' else parts[0]
                            })
        except Exception as e:
            print(f"Error getting images: {e}")
        
        return sorted(images, key=lambda x: x['size_bytes'], reverse=True)
    
    def get_container_info(self) -> List[Dict]:
        """Get information about containers and their space usage."""
        containers = []
        try:
            result = subprocess.run(['docker', 'ps', '-a', '--format', 
                                   '{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Size}}\t{{.CreatedAt}}'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('\t')
                        if len(parts) >= 5:
                            containers.append({
                                'name': parts[0],
                                'image': parts[1],
                                'status': parts[2],
                                'size': parts[3],
                                'created': parts[4]
                            })
        except Exception as e:
            print(f"Error getting containers: {e}")
        
        return containers
    
    def _parse_size_to_bytes(self, size_str: str) -> int:
        """Convert Docker size string to bytes for sorting."""
        size_str = size_str.strip()
        if not size_str or size_str == '0B':
            return 0
        
        # Extract number and unit
        match = re.match(r'^([0-9.]+)\s*([KMGTPB]+)', size_str)
        if not match:
            return 0
        
        number = float(match.group(1))
        unit = match.group(2).upper()
        
        multipliers = {
            'B': 1,
            'KB': 1024,
            'MB': 1024**2,
            'GB': 1024**3,
            'TB': 1024**4,
            'PB': 1024**5
        }
        
        return int(number * multipliers.get(unit, 1))
    
    def identify_comfyui_components(self, images: List[Dict]) -> List[Dict]:
        """Identify ComfyUI-related images and containers."""
        comfyui_keywords = ['comfy', 'comfyui', 'stable-diffusion', 'pytorch', 'cuda', 'ml', 'ai-image']
        comfyui_items = []
        
        for image in images:
            repo_lower = image['repository'].lower()
            if any(keyword in repo_lower for keyword in comfyui_keywords):
                image['category'] = 'ComfyUI/AI'
                comfyui_items.append(image)
        
        return comfyui_items
    
    def generate_cleanup_recommendations(self, images: List[Dict], containers: List[Dict]) -> Dict:
        """Generate intelligent cleanup recommendations."""
        recommendations = {
            'immediate_cleanup': [],
            'safe_to_remove': [],
            'space_hogs': [],
            'unused_images': [],
            'old_containers': []
        }
        
        # Find space hogs (>5GB)
        for image in images:
            if image['size_bytes'] > 5 * 1024**3:  # 5GB
                recommendations['space_hogs'].append({
                    'name': image['full_name'],
                    'size': image['size_str'],
                    'reason': 'Large image consuming significant space'
                })
        
        # Find dangling/unused images
        used_images = {container['image'] for container in containers}
        for image in images:
            if image['full_name'] not in used_images and '<none>' not in image['repository']:
                if image['size_bytes'] > 1024**3:  # >1GB
                    recommendations['unused_images'].append({
                        'name': image['full_name'],
                        'size': image['size_str'],
                        'reason': 'Large unused image'
                    })
        
        # Find stopped/old containers
        for container in containers:
            if 'Exited' in container['status']:
                recommendations['old_containers'].append({
                    'name': container['name'],
                    'image': container['image'],
                    'status': container['status'],
                    'reason': 'Stopped container taking space'
                })
        
        return recommendations
    
    def calculate_potential_savings(self, recommendations: Dict, images: List[Dict]) -> Dict:
        """Calculate potential space savings from cleanup."""
        savings = {
            'unused_images_gb': 0,
            'old_containers_gb': 0,
            'total_potential_gb': 0
        }
        
        # Calculate unused image savings
        for rec in recommendations['unused_images']:
            for image in images:
                if image['full_name'] == rec['name']:
                    savings['unused_images_gb'] += image['size_bytes'] / (1024**3)
                    break
        
        # Estimate container overhead (rough estimate)
        savings['old_containers_gb'] = len(recommendations['old_containers']) * 0.1  # 100MB per container
        
        savings['total_potential_gb'] = savings['unused_images_gb'] + savings['old_containers_gb']
        
        return savings
    
    def run_analysis(self) -> Dict:
        """Run complete Docker space analysis."""
        print("🔍 Analyzing Docker space usage...")
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'system_info': self.get_docker_system_info(),
            'images': self.get_detailed_images(),
            'containers': self.get_container_info(),
        }
        
        # Identify ComfyUI components
        analysis['comfyui_components'] = self.identify_comfyui_components(analysis['images'])
        
        # Generate recommendations
        analysis['recommendations'] = self.generate_cleanup_recommendations(
            analysis['images'], analysis['containers'])
        
        # Calculate savings
        analysis['potential_savings'] = self.calculate_potential_savings(
            analysis['recommendations'], analysis['images'])
        
        # Save analysis
        with open(self.analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        return analysis
    
    def print_analysis_report(self, analysis: Dict):
        """Print formatted analysis report."""
        print("\n" + "="*60)
        print("🐳 DOCKER SPACE ANALYSIS REPORT")
        print("="*60)
        
        # System overview
        system_info = analysis.get('system_info', {})
        if system_info:
            print(f"\n💾 System Overview:")
            for item in system_info.get('data', []):
                if item.get('Type') == 'Images':
                    print(f"   Images: {item.get('Size', 'Unknown')} ({item.get('Reclaimable', '0B')} reclaimable)")
                elif item.get('Type') == 'Containers':
                    print(f"   Containers: {item.get('Size', 'Unknown')}")
                elif item.get('Type') == 'Local Volumes':
                    print(f"   Volumes: {item.get('Size', 'Unknown')}")
        
        # Top space consumers
        print(f"\n🔥 Top 10 Largest Images:")
        for i, image in enumerate(analysis['images'][:10], 1):
            print(f"   {i:2d}. {image['size_str']:>8} - {image['full_name']}")
        
        # ComfyUI analysis
        comfyui_items = analysis['comfyui_components']
        if comfyui_items:
            print(f"\n🎨 ComfyUI/AI Related Images ({len(comfyui_items)} found):")
            comfyui_total = sum(item['size_bytes'] for item in comfyui_items)
            print(f"   Total ComfyUI space: {comfyui_total / (1024**3):.1f} GB")
            for item in comfyui_items[:5]:
                print(f"   • {item['size_str']:>8} - {item['full_name']}")
        
        # Cleanup recommendations
        recommendations = analysis['recommendations']
        savings = analysis['potential_savings']
        
        print(f"\n💡 Cleanup Recommendations:")
        print(f"   Potential savings: {savings['total_potential_gb']:.1f} GB")
        
        if recommendations['space_hogs']:
            print(f"\n🐘 Space Hogs (>5GB each):")
            for item in recommendations['space_hogs'][:5]:
                print(f"   • {item['size']:>8} - {item['name']}")
        
        if recommendations['unused_images']:
            print(f"\n🗑️  Unused Images ({savings['unused_images_gb']:.1f} GB recoverable):")
            for item in recommendations['unused_images'][:5]:
                print(f"   • {item['size']:>8} - {item['name']}")
        
        if recommendations['old_containers']:
            print(f"\n⏹️  Stopped Containers ({len(recommendations['old_containers'])} found):")
            for item in recommendations['old_containers'][:5]:
                print(f"   • {item['name']} ({item['image']})")
        
        print(f"\n📋 Cleanup Commands:")
        print(f"   # Remove unused images:")
        for item in recommendations['unused_images'][:3]:
            print(f"   docker rmi {item['name']}")
        
        print(f"\n   # Remove stopped containers:")
        print(f"   docker container prune -f")
        
        print(f"\n   # Nuclear option (careful!):")
        print(f"   docker system prune -a")
        
        print(f"\n📊 Analysis saved to: {self.analysis_file}")
        print("="*60)

def main():
    analyzer = DockerSpaceAnalyzer()
    
    try:
        analysis = analyzer.run_analysis()
        analyzer.print_analysis_report(analysis)
        
        print(f"\n🎯 Key Insights:")
        
        # Special insight about ComfyUI
        comfyui_items = analysis['comfyui_components']
        if comfyui_items:
            comfyui_space = sum(item['size_bytes'] for item in comfyui_items) / (1024**3)
            print(f"   • ComfyUI using {comfyui_space:.1f} GB - consider separate repo project")
        
        savings = analysis['potential_savings']['total_potential_gb']
        if savings > 5:
            print(f"   • {savings:.1f} GB easily recoverable through cleanup")
        elif savings > 1:
            print(f"   • {savings:.1f} GB potentially recoverable")
        else:
            print(f"   • System is fairly optimized already")
            
        print(f"   • Run 'docker system prune -a' to clean up safely")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        print("💡 Make sure Docker is running and try again")

if __name__ == "__main__":
    main()