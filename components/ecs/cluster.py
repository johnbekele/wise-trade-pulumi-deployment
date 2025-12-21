import pulumi
from pulumi_aws import ecs
from pydantic import BaseModel
from typing import Optional, Dict, List



class EcsCluster(pulumi.ComponentResource):
    def __init__(
            self,
            name,
            tags:Optional[Dict[str, str]] = None,
            opts=None):
        super().__init__("custom:ecs:Cluster" ,name ,None ,opts)

        self.cluster=ecs.Cluster(
            f"{name}-cluster", 
             tags=tags,
            opts=pulumi.ResourceOptions(parent=self)
            )
        
        self.register_outputs(
            {
                "cluster_arn":self.cluster.arn
            }
        )