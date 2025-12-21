"""An AWS Python Pulumi program"""

import pulumi
from pulumi import Config
from pulumi_aws import s3

#Components

from components.network.vpc import Vpc ,VpcArgs
from components.network.security_group import SecurityGroups
from components.alb import Alb
from components.ecs.cluster import EcsCluster
from components.ecs.service import EcsService, EcsServiceArgs
from components.ecs.task import TaskDefinition , TaskArgs


config=Config()
mongo_uri="https://"+config.require("mongoUri")
frontend_image=config.require("frontend_image")
backend_image=config.require("backend_image")
project_name=config.require("project_name")

tags={
    "project":"wise-trader",
    "owner":"john bekele",
    "environment":"dev"
}
#===============================================================================
# Network setup
#===============================================================================
args=VpcArgs(
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags=tags
)

vpc=Vpc(project_name,args)

#===============================================================================
# Security Groups
#===============================================================================
sg=SecurityGroups(
    project_name,
    vpc_id=vpc.vpc.id,

)

#===============================================================================
# Application Load Balancer
#===============================================================================
alb=Alb(
    project_name,
    vpc_id=vpc.vpc.id,
    public_subnets=vpc.public_subnets,
    alb_sg=sg.alb_sg,
    tags=tags
)

#===============================================================================
# ECS Cluster
#===============================================================================
ecs_cluster=EcsCluster(
    project_name,
    tags=tags
)
#===============================================================================
# ECS Task Definition
#===============================================================================
task=TaskDefinition(
    project_name,
    args=TaskArgs(
        mongo_uri=mongo_uri,
        frontend_image=frontend_image,
        backend_image=backend_image,
    
    ))
#===============================================================================
# ECS Service
#===============================================================================
ecs_service=EcsService(
    project_name,
    cluster_arn=ecs_cluster.cluster.arn,
    task_def_arn=task.task_def.arn,
    private_subnets=[subnet.id for subnet in vpc.private_subnets],
    ecs_sg=sg.ecs_sg.id,
    target_group_arn=alb.target_group.arn,
    args=EcsServiceArgs(
        desired_count=1
    ))


pulumi.export("url", alb.alb.dns_name)