#!/opt/homebrew/opt/node/bin/node
// See https://docs.aws.amazon.com/cdk/v2/guide/build-containers.html
import * as cdk from 'aws-cdk-lib';
import { DangerMondNextGenStack } from '../lib/stack';

const app = new cdk.App();
new DangerMondNextGenStack(app, 'DangermondNextGen');