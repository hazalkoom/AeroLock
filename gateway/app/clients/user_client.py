import grpc
from fastapi import HTTPException
from aerolock_common.generated import user_pb2, user_pb2_grpc
from aerolock_common.logging import setup_logger

logger = setup_logger("gateway-user-client")

class UserClient:
    def __init__(self, host='user-service', port=50053):
        self.channel = grpc.aio.insecure_channel(f'{host}:{port}')
        self.stub = user_pb2_grpc.UserServiceStub(self.channel)

    async def register(self, email, password, first_name, last_name):
        try:
            req = user_pb2.RegisterRequest(
                email=email, password=password, first_name=first_name, last_name=last_name
            )
            resp = await self.stub.RegisterUser(req)
            if not resp.success:
                raise HTTPException(status_code=400, detail=resp.message)
            return {"access_token": resp.access_token, "user_id": resp.user_id, "message": resp.message}
        except grpc.aio.AioRpcError as e:
            logger.error(f"gRPC Error in register: {e.details()}")
            raise HTTPException(status_code=500, detail="Internal Auth Service Error")

    async def login(self, email, password):
        try:
            req = user_pb2.LoginRequest(email=email, password=password)
            resp = await self.stub.LoginUser(req)
            if not resp.success:
                raise HTTPException(status_code=401, detail=resp.message)
            return {"access_token": resp.access_token, "user_id": resp.user_id, "message": resp.message}
        except grpc.aio.AioRpcError as e:
            logger.error(f"gRPC Error in login: {e.details()}")
            raise HTTPException(status_code=500, detail="Internal Auth Service Error")

    async def get_profile(self, user_id):
        try:
            req = user_pb2.GetProfileRequest(user_id=user_id)
            resp = await self.stub.GetProfile(req)
            return {
                "id": resp.id,
                "email": resp.email,
                "first_name": resp.first_name,
                "last_name": resp.last_name,
                "role": resp.role
            }
        except grpc.aio.AioRpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                raise HTTPException(status_code=404, detail="User not found")
            logger.error(f"gRPC Error in get_profile: {e.details()}")
            raise HTTPException(status_code=500, detail="Internal Auth Service Error")