# pylint: disable=line-too-long
from rest_framework import status
from rest_framework.exceptions import APIException


class CustomAPIException(APIException):
    use_custom_handler = True
    default_code = None

    def __init__(self, detail=None, status_code=None, code=None):
        super().__init__(None, None)

        if detail is not None:
            self.default_detail = detail
        if code is not None:
            self.default_code = code
        if status_code is not None:
            self.status_code = status_code


class WrongCredentialsException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Email or password is incorrect."
    default_code = 1000


class UnverifiedEmailException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "This email has not verified yet."
    default_code = 1001


class AssigningDriverNotFoundException(CustomAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "All Drivers are busy."
    default_code = 1002


class AutoAssignConflictException(CustomAPIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Data conflict."
    default_code = 1003


class WrongAssociatedAccountException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "This email address is already associated to Google, Facebook, Apple ID or Phone number"
    default_code = 1004


class SSOMissingEmailAddressException(CustomAPIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "There is no email address associated with this account."
    default_code = 1005


class DeactivateAccountTaskDeniedException(CustomAPIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Please clear your to-do tasks before deleting your account."
    default_code = 1006


class EmailHasBeenVerifiedException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Email has been verified."
    default_code = 1007


class InvalidTokenException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid token."
    default_code = 1008


class EmailNotFoundException(CustomAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Email not found."
    default_code = 1009


class ResetPasswordExpiredException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Your password reset link has expired."
    default_code = 1010


class UniqueException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Dupplicate entry."
    default_code = 1011


class SomethingWentWrongException(CustomAPIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Something went wrong."
    default_code = 1012


class InvalidPhoneNumberException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Please check your phone number again!"
    default_code = 1013


class InvalidRequestException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid request."
    default_code = 1014


class UnableVerifyPhoneNumberException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Unable to verify phone number."
    default_code = 1015


class PhoneWrongAssociatedAccountException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "This phone number is already associated with an account."
    default_code = 1016


class PhoneNotRegisteredException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "This is not a registered number, please check again."
    default_code = 1017


class PhoneRegisteredException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "This is a registered number, please check again."
    default_code = 1018


class NoAccountFoundException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "We couldn't find your account, please check again."
    default_code = 1019


class PhoneChangeIncorrectSafetyQuestionException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Date of birth or postal code is incorrect."
    default_code = 1020


class PhoneChangeVerificationTokenNotFoundException(CustomAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Phone change verification token not found."
    default_code = 1021


class UpdateExistingEmailUserConflictException(CustomAPIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Unable to update email to User who has an existing email."
    default_code = 1022


class EmailHasBeenRegisteredException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "This email has been registered."
    default_code = 1023


class TasksIsCompletedOrNotPickUpStatusException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Task(s) are completed or are not Pick-up status."
    default_code = 1024


class DuplicateOrderStoreOrganizationException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "This pair of store_id and organization_id is duplicated"
    default_code = 1025


class UserNotFoundException(CustomAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "User Not Found"
    default_code = 1026


class UserIsDeactivatedException(CustomAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "User is deactivated"
    default_code = 1027


class CredentialsLinkedToEmailPasswordLoginException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Your credentials are already linked to email/password login, please use email login instead"
    default_code = 1028


class EditRejectedUserException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Edit rejected user"
    default_code = 1029


class PickupSpotAlreadyExistsException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Pickup spot with this latitude and longitude already exists"
    default_code = 1030


class DriverIsSuspendedException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Driver is suspended."
    default_code = 1031


class ThirdPartyDriverPoolExistException(CustomAPIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "There is an existing Third-Party Driver Pool"
    default_code = 1032


class DeactivateDriverHoldingDeliveringTasksException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = (
        "Can not deactivate this driver because he/she is holding delivering task."
    )
    default_code = 1033


class TaskNotFoundException(CustomAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Task not found."
    default_code = 1034


class DriverPoolNotFound(CustomAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Driver pool not found"
    default_code = 1035


class NotFoundCoordinateFromAddressException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Cannot find coordinate from given address"
    default_code = 1036


class ConvertAddressCoordinateException(CustomAPIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Exception when convert address to coordinate"
    default_code = 1037


class ErrorUpdateCourierOrderException(CustomAPIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Errors occur when update Courier order"
    default_code = 1038


class InvalidTaskSourceException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid task source."
    default_code = 1039


class CancelTaskException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Task does not cancel because it is assigned to one driver."
    default_code = 1040


class TaskAssignedException(CustomAPIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Task has been assigned to driver. Please refresh the page !"
    default_code = 1041


class CourierConnectionFailException(CustomAPIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Courier connection fail."
    default_code = 1042


class FacebookNotLinkedToEmailException(CustomAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Facebook account is not linked to an email."
    default_code = 1043


class UnknownTimezoneException(CustomAPIException):
    # TODO: this exception is not used, remove it later
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Unknown timezone."
    default_code = 1044


class DriverNotAvailableException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Driver is not available or not active."
    default_code = 1045


class DriverReachMaxOnGoingTaskException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Driver does reach the limitation of ongoing tasks."
    default_code = 1046


class DriverOfflineException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Driver is offline."
    default_code = 1047


class DriverIsExcludedFromTaskException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Driver is excluded from task."
    default_code = 1048


class DriverWorkingScheduleNotMatchException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Working schedule is not match."
    default_code = 1049


class DriverIsDeletedException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Driver is deleted."
    default_code = 1050


class DriverProfileIsNotVerifiedException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Driver'profile is not verified."
    default_code = 1051


class PreferredAreaNotMatchWorkingHour(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Not match working hour."
    default_code = 1052


class PreferredAreaNotMatchWorkingDay(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Not match working day."
    default_code = 1053


class PreferredAreaNotMatchDistance(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Selected task(s) mismatches driver’s working preference. Please select a different driver."
    default_code = 1054


class CannotGetWarehouseCoordinatesException(CustomAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Can not get warehouse's coordinates."
    default_code = 1055


class CannotConnectToTrackingLocationException(CustomAPIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Can not connect to Tracking location."
    default_code = 1056


class CannotGetOnlineDriversException(CustomAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Can not get online drivers from Tracking location."
    default_code = 1057


class DriverProfileIsRejectedException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Driver’s profile is rejected."
    default_code = 1058


class DriverAndTaskSourceNotMatchDriverPoolException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Task source and driver do not match driver pool."
    default_code = 1059


class SpecifyDriverException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Not specify driver in task Courier"
    default_code = 1061


class InvalidPercentageRatesException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Percentage rates must be level 1 <= level 2 <= level 3."
    default_code = 1062


class InvalidCommissionRateIDException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "CommissionRate with this ID doesn't exist."
    default_code = 1063


class DetailSpecifyDriverException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 1064


class TaskWarehouseNotLinkedDriverPool(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "This pool has not linked to the warehouse yet"
    default_code = 1065


class DateFormatException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Date incorrect query format."
    default_code = 1066


class ConvertCoordinateToTimezoneException(CustomAPIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Exception when convert coordinate to timezone"
    default_code = 1067


class ConflictFilterPendingDateException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Please choose filter only by ordered date or delivery date"
    default_code = 1068


class CredentialsLinkedToPhoneLoginException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Your credentials are already linked to phone login, please use phone login instead"
    default_code = 1069


class SMSNotSendException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "The SMS does not send."
    default_code = 1070


class CallItADayException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Day is not today"
    default_code = 1071


class TimezoneException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Not found driver timezone"
    default_code = 1071


class NotFoundDriverException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Not found driver with id"
    default_code = 1072


class MultipleTasksPickupNotFoundException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Not found tasks to pick up."
    default_code = 1073


class TaskExistsException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Task is already exists."
    default_code = 1075


class TaskNotInScheduledTimeException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Task is not in scheduled time."
    default_code = 1074


class APIConnectionFailedException(CustomAPIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "API connection failed."
    default_code = 1075


class PlaceSearchFailedException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Can not find your place."
    default_code = 1076


class GetPlaceDetailsFailedException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Can not find place details."
    default_code = 1077


class SettingNotFoundException(CustomAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Setting not found."
    default_code = 1078


class InvalidPaidStatusException(CustomAPIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Invalid billing paid status."
    default_code = 1079


class InvalidDriverPoolException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid driver pool."
    default_code = 1080


class InvalidCourierTaskException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Task is not a courier task."
    default_code = 1081


class TaskWarehouseNotLinkedDriverPools(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "This pool has not linked to the warehouse yet. Please check again"
    default_code = 1082


class TaskCancelled(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Task is cancelled."
    default_code = 1083


class NoPreferredAreaMatched(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "No matched preferred area."
    default_code = 1084


class InvalidTimeStartException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Time start is not correct or invalid."
    default_code = 1085


class InvalidCoordinateException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "The coordinate is not correct or invalid."
    default_code = 1086


class InvalidUserForDeleteNote(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid user for delete notes"
    default_code = 1087


class DeniedAssignFutureOrder(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "This is future order, cannot assign."
    default_code = 1088


class NotFutureOrder(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "This is not a future order, cannot pre-assign driver."
    default_code = 1089


class OrderScheduleAlreadyStarted(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Order already started finding driver, cannot pre-assign."
    default_code = 1090


class TasksIsCompletedOrCanceled(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Task(s) are completed or has been canceled."
    default_code = 1091
