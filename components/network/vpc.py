import pulumi
from pulumi_aws import ec2
import pulumi_aws
from pydantic import BaseModel
from typing import Optional, Dict, List


class VpcArgs(BaseModel):
    cidr_block: str
    enable_dns_support: Optional[bool] = True
    enable_dns_hostnames: Optional[bool] = True
    tags: Optional[Dict[str, str]] = None
    public_ip_on_launch: bool = True


class Vpc(pulumi.ComponentResource):
    def __init__(self, name: str, args: VpcArgs, opts: Optional[pulumi.ResourceOptions] = None):
        super().__init__("custom:network:Vpc", name, None, opts)
       
        tags= lambda merge: {**(args.tags or {}),"Name": f"{name}-vpc"}
        # Create VPC
        self.vpc = ec2.Vpc(
            f"{name}-vpc",
            cidr_block=args.cidr_block,
            enable_dns_support=args.enable_dns_support,
            enable_dns_hostnames=args.enable_dns_hostnames,
            tags=tags(f"{name}-vpc"),
            opts=pulumi.ResourceOptions(parent=self)
        )

        # Availability zones (first 2)
        azs = pulumi_aws.get_availability_zones().names[:2]

        self.public_subnets: List[ec2.Subnet] = []
        self.private_subnets: List[ec2.Subnet] = []

        # Create subnets
        for i, az in enumerate(azs):
            self.public_subnets.append(
                ec2.Subnet(
                    f"{name}-public-subnet-{i}",
                    vpc_id=self.vpc.id,
                    cidr_block=f"10.0.{i}.0/24",
                    availability_zone=az,
                    map_public_ip_on_launch=args.public_ip_on_launch,
                    tags=args.tags or {"Name": f"{name}-public-{i}"},
                    opts=pulumi.ResourceOptions(parent=self)
                )
            )

            self.private_subnets.append(
                ec2.Subnet(
                    f"{name}-private-subnet-{i}",
                    vpc_id=self.vpc.id,
                    cidr_block=f"10.0.{i+10}.0/24",
                    availability_zone=az,
                    map_public_ip_on_launch=False,
                    tags=args.tags or {"Name": f"{name}-private-{i}"},
                    opts=pulumi.ResourceOptions(parent=self)
                )
            )

        # Internet Gateway
        self.igw = ec2.InternetGateway(
            f"{name}-igw",
            vpc_id=self.vpc.id,
            tags=args.tags or {"Name": f"{name}-igw"},
            opts=pulumi.ResourceOptions(parent=self)
        )

        # Public route table
        self.public_rt = ec2.RouteTable(
            f"{name}-public-rt",
            vpc_id=self.vpc.id,
            routes=[{
                "cidr_block": "0.0.0.0/0",
                "gateway_id": self.igw.id
            }],
            tags=args.tags or {"Name": f"{name}-public-rt"},
            opts=pulumi.ResourceOptions(parent=self)
        )

        # Associate public subnets with the public route table
        for i, subnet in enumerate(self.public_subnets):
            ec2.RouteTableAssociation(
                f"{name}-public-rt-assoc-{i}",
                subnet_id=subnet.id,
                route_table_id=self.public_rt.id,
                opts=pulumi.ResourceOptions(parent=self)
            )

        # Outputs
        self.register_outputs({
            "vpc_id": self.vpc.id,
            "public_subnets": [s.id for s in self.public_subnets],
            "private_subnets": [s.id for s in self.private_subnets]
        })
