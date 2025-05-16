import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ecr_assets from 'aws-cdk-lib/aws-ecr-assets';
import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as ecs from "aws-cdk-lib/aws-ecs";
import * as elbv2 from "aws-cdk-lib/aws-elasticloadbalancingv2"
import * as ecs_patterns from "aws-cdk-lib/aws-ecs-patterns";
import * as cert from "aws-cdk-lib/aws-certificatemanager";


const certificateArn = 
  'arn:aws:acm:us-west-1:719729260530:certificate/' + 
  'a30ce00b-0761-4786-879f-c03af057512a'


export class DangerMondNextGenStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id);
  
    // Define the Docker image asset
    const dockerImageAsset = new ecr_assets.DockerImageAsset(this, 'MyDockerImage', {
      directory: '../', // Path to the directory containing the Dockerfile
      exclude: ['aws*']
    });
  
    // Output the ECR URI
    new cdk.CfnOutput(this, 'ECRImageUri', {
      value: dockerImageAsset.imageUri,
    });

    // create VPC
    const vpc = new ec2.Vpc(this, "MyVpc", {
      maxAzs: 3 // Default is all AZs in region
    });

    // create Cluster
    const cluster = new ecs.Cluster(this, "MyCluster", {
      vpc: vpc
    });

    // see https://stackoverflow.com/questions/60040605/how-to-import-custom-cerficate-using-aws-cdk#:~:text=Since%20CDK%20generates%20cloudformation%20stack%20behind%20the%20senses%2C,the%20certificate%20ARN.%20Usage%3A%20More%20info%20about%20cert.Certificate.
    const certificate = cert.Certificate.fromCertificateArn(
      this, 'manuallyCreatedCert', certificateArn)

    // Create a load-balanced Fargate service and make it public
    new ecs_patterns.ApplicationLoadBalancedFargateService(this, "MyFargateService", {
      serviceName: "DangermondNextGen",
      cluster: cluster, // Required
      cpu: 512, // Default is 256
      desiredCount: 1, // Default is 1
      minHealthyPercent: 100,
      taskImageOptions: { 
        image: ecs.ContainerImage.fromDockerImageAsset(dockerImageAsset),
        containerPort: 10000,
        environment: {
          aws_access_key_id: process.env.AWS_ACCESS_KEY_ID || '', 
          aws_secret_access_key: process.env.AWS_SECRET_ACCESS_KEY || '',
          BUCKET_NAME: 'dangermond-nextgen'
        }
      },
      certificate: certificate, 
      redirectHTTP: true,
      memoryLimitMiB: 2048, // Default is 512
      publicLoadBalancer: true, // Default is true
      protocol: elbv2.ApplicationProtocol.HTTPS,
      healthCheck: {
        command: ["CMD-SHELL", "curl -f http://localhost:10000/ || exit"]
      }
    });

  }
}
