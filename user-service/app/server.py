import grpc
import asyncio
from aerolock_common.logging import setup_logger
from aerolock_common.generated import user_pb2, user_pb2_grpc
from app.core.db import AsyncSessionLocal
from app.db.repository import UserRepository
from app.core.security import verify_password, create_access_token

logger = setup_logger("user-service")

class UserService(user_pb2_grpc.UserServiceServicer):
    
    async def RegisterUser(self, request, context):
        logger.info(f"Attempting to register user: {request.email}")
        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)
            success, result = await repo.create_user(
                email=request.email,
                password=request.password,
                first_name=request.first_name,
                last_name=request.last_name
            )
            
            if not success:
                logger.warning(f"Registration failed for {request.email}: {result}")
                return user_pb2.AuthResponse(
                    success=False, 
                    access_token="", 
                    message=result,
                    user_id=""
                )
                
            token = create_access_token(result.id, result.role)
            logger.info(f"User registered successfully: {result.id}")
            return user_pb2.AuthResponse(
                success=True, 
                access_token=token, 
                message="User registered successfully", 
                user_id=str(result.id)
            )

    async def LoginUser(self, request, context):
        logger.info(f"Login attempt for user: {request.email}")
        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)
            user = await repo.get_user_by_email(request.email)
            
            if not user or not await verify_password(request.password, user.password_hash):
                logger.warning(f"Failed login attempt for {request.email}")
                return user_pb2.AuthResponse(
                    success=False, 
                    access_token="", 
                    message="Invalid email or password", 
                    user_id=""
                )
                
            token = create_access_token(user.id, user.role)
            logger.info(f"Login successful for user: {user.id}")
            return user_pb2.AuthResponse(
                success=True, 
                access_token=token, 
                message="Login successful", 
                user_id=str(user.id)
            )

    async def GetProfile(self, request, context):
        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)
            user = await repo.get_user_by_id(request.user_id)
            
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("User not found")
                return user_pb2.UserProfileResponse()
                
            return user_pb2.UserProfileResponse(
                id=str(user.id),
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role
            )

async def serve():
    server = grpc.aio.server()
    user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    listen_addr = '[::]:50053'
    server.add_insecure_port(listen_addr)
    logger.info(f"Starting User Service on {listen_addr}...")
    
    await server.start()
    await server.wait_for_termination()

if __name__ == '__main__':
    asyncio.run(serve())