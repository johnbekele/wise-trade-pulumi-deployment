import pulumi
from pulumi_aws import ecs
from pydantic import BaseModel
from typing import Optional, Dict, List




class ClusterArgs(BaseModel):
    vpc_id: str
    private_subnets: List[str]
    ecs_security_group: str
    tags: Optional[Dict[str, str]] = None


class EcsCluster(pulumi.ComponentResource):
    def __init__(self,name,args:ClusterArgs,opts=None):
        super().__init__("custome:ecs:Cluster" ,name ,None ,opts)

        self.cluster=ecs.Cluster(
            f"{name}-cluster", 
             tags=args.tags,
            opts=pulumi.ResourceOptions(parent=self)
            )
        
        self.register_outputs(
            {
                "cluster_arn":self.cluster.arn
            }
        )