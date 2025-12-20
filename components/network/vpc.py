import pulumi 
from pulumi_aws import aws 
from pydantic import BaseModel
from typing import Optional, List


class VpcArgs(BaseModel):
    name: str
    cidr_block: str
    enable_dns_support: Optional[bool] = True
    enable_dns_hostnames: Optional[bool] = True
    tags: Optional[dict] = None
    public_subnets:List 
    private_subnets:List
    public_ip_on_launch: bool = True


class Vpc(pulumi.ComponentResource):
    def __init__(self,name, args: VpcArgs, opts: Optional[pulumi.ResourceOptions] = None):
        super().__init__('custom:network:Vpc', name, None, opts)

        self.vpc = aws.ec2.Vpc(
            f"{name}-vpc",
            resource_name=name,
            cidr_block=args.cidr_block,
            enable_dns_support=args.enable_dns_support,
            enable_dns_hostnames=args.enable_dns_hostnames,
            tags=args.tags or {"Name": name},
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        #availability zones
        azs= aws.get_availability_zones(state="available").names[:2]
        
        self.public_subnets = []
        self.private_subnets = []
        
        for i, az in enumerate(azs):
            self.public_subnets.append(
                aws.ec2.Subnet(
                    f"{name}-public-subnet-{i}",
                    vpc_id=self.vpc.id,
                    cidr_block=f"10.0.{i}.0/24",
                    availabilitiy_zone= az,
                    map_public_ip_on_launch=args.public_ip_on_launch ,
                    opts=pulumi.ResourceOptions(parent=self))
            )

            self.private_subnets.append(
                aws.ec2.Subnet(
                    f"{name}-private-subnet-{i}",
                    vpc_id=self.vpc.id,
                    cidr_block=f"10.0.{i}.0/24",
                    availabilitiy_zone= az,
                    map_public_ip_on_launch=args.public_ip_on_launch ,
                    opts=pulumi.ResourceOptions(parent=self)

                )
            )

        
        self.register_outputs({
            "vpc_id": self.vpc.id,
            "cidr_block": self.vpc.cidr_block,
            "public_subnets":self.public_subnets,
            "private_subnets":self.private_subnets
        })