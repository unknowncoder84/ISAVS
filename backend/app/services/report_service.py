"""
Report Service
Handles attendance reporting, statistics, and anomaly aggregation.
"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.db.models import (
    AttendanceORM, StudentORM, AnomalyORM, 
    AttendanceSessionORM, ClassORM, ClassEnrollmentORM
)
from app.models.schemas import (
    AttendanceRecord, ProxyAlert, IdentityMismatchAlert,
    AttendanceStatistics, ReportResponse
)


class ReportService:
    """Service for generating attendance reports and statistics."""
    
    async def get_attendance_records(
        self,
        db: AsyncSession,
        session_id: Optional[int] = None,
        student_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100
    ) -> List[AttendanceRecord]:
        """
        Get attendance records with optional filters.
        """
        query = (
            select(AttendanceORM, StudentORM)
            .join(StudentORM, AttendanceORM.student_id == StudentORM.id)
        )
        
        conditions = []
        
        if session_id:
            conditions.append(AttendanceORM.session_id == session_id)
        
        if student_id:
            conditions.append(AttendanceORM.student_id == student_id)
        
        if start_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            conditions.append(AttendanceORM.timestamp >= start_datetime)
        
        if end_date:
            end_datetime = datetime.combine(end_date, datetime.max.time())
            conditions.append(AttendanceORM.timestamp <= end_datetime)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(AttendanceORM.timestamp.desc()).limit(limit)
        
        result = await db.execute(query)
        rows = result.all()
        
        records = []
        for attendance, student in rows:
            records.append(AttendanceRecord(
                id=attendance.id,
                student_id=student.id,
                student_name=student.name,
                student_id_card_number=student.student_id_card_number,
                timestamp=attendance.timestamp,
                verification_status=attendance.verification_status,
                face_confidence=attendance.face_confidence,
                otp_verified=attendance.otp_verified
            ))
        
        return records
    
    async def get_attendance_by_date(
        self,
        db: AsyncSession,
        target_date: date
    ) -> List[AttendanceRecord]:
        """
        Get all attendance records for a specific date.
        """
        return await self.get_attendance_records(
            db=db,
            start_date=target_date,
            end_date=target_date,
            limit=1000
        )
    
    async def calculate_attendance_percentage(
        self,
        db: AsyncSession,
        student_id: int,
        class_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> float:
        """
        Calculate attendance percentage for a student.
        
        Returns percentage as float (0-100).
        """
        # Count verified attendance
        verified_query = select(func.count(AttendanceORM.id)).where(
            and_(
                AttendanceORM.student_id == student_id,
                AttendanceORM.verification_status == 'verified'
            )
        )
        
        # Count total sessions the student should have attended
        total_query = select(func.count(AttendanceSessionORM.id))
        
        if class_id:
            # Filter by class enrollment
            total_query = total_query.join(
                ClassEnrollmentORM,
                and_(
                    ClassEnrollmentORM.class_id == AttendanceSessionORM.class_id,
                    ClassEnrollmentORM.student_id == student_id
                )
            ).where(AttendanceSessionORM.class_id == class_id)
        
        if start_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            verified_query = verified_query.where(AttendanceORM.timestamp >= start_datetime)
            total_query = total_query.where(AttendanceSessionORM.started_at >= start_datetime)
        
        if end_date:
            end_datetime = datetime.combine(end_date, datetime.max.time())
            verified_query = verified_query.where(AttendanceORM.timestamp <= end_datetime)
            total_query = total_query.where(AttendanceSessionORM.started_at <= end_datetime)
        
        verified_result = await db.execute(verified_query)
        verified_count = verified_result.scalar() or 0
        
        total_result = await db.execute(total_query)
        total_count = total_result.scalar() or 0
        
        if total_count == 0:
            return 0.0
        
        percentage = (verified_count / total_count) * 100
        return round(percentage, 2)
    
    async def get_proxy_alerts(
        self,
        db: AsyncSession,
        session_id: Optional[int] = None,
        limit: int = 50
    ) -> List[ProxyAlert]:
        """
        Get proxy attempt alerts.
        """
        query = (
            select(AnomalyORM, StudentORM)
            .outerjoin(StudentORM, AnomalyORM.student_id == StudentORM.id)
            .where(AnomalyORM.anomaly_type == 'proxy_attempt')
        )
        
        if session_id:
            query = query.where(AnomalyORM.session_id == session_id)
        
        query = query.order_by(AnomalyORM.timestamp.desc()).limit(limit)
        
        result = await db.execute(query)
        rows = result.all()
        
        alerts = []
        for anomaly, student in rows:
            alerts.append(ProxyAlert(
                id=anomaly.id,
                student_id=anomaly.student_id,
                student_name=student.name if student else None,
                reason=anomaly.reason,
                timestamp=anomaly.timestamp
            ))
        
        return alerts
    
    async def get_identity_mismatch_alerts(
        self,
        db: AsyncSession,
        session_id: Optional[int] = None,
        limit: int = 50
    ) -> List[IdentityMismatchAlert]:
        """
        Get identity mismatch alerts (OTP correct but face < 0.6).
        """
        query = (
            select(AnomalyORM, StudentORM)
            .join(StudentORM, AnomalyORM.student_id == StudentORM.id)
            .where(AnomalyORM.anomaly_type == 'identity_mismatch')
        )
        
        if session_id:
            query = query.where(AnomalyORM.session_id == session_id)
        
        query = query.order_by(AnomalyORM.timestamp.desc()).limit(limit)
        
        result = await db.execute(query)
        rows = result.all()
        
        alerts = []
        for anomaly, student in rows:
            alerts.append(IdentityMismatchAlert(
                id=anomaly.id,
                student_id=student.id,
                student_name=student.name,
                face_confidence=anomaly.face_confidence or 0.0,
                timestamp=anomaly.timestamp
            ))
        
        return alerts
    
    async def get_attendance_statistics(
        self,
        db: AsyncSession,
        session_id: Optional[int] = None,
        class_id: Optional[int] = None
    ) -> AttendanceStatistics:
        """
        Get attendance statistics for a session or class.
        """
        # Get total enrolled students
        if class_id:
            total_query = select(func.count(ClassEnrollmentORM.id)).where(
                ClassEnrollmentORM.class_id == class_id
            )
        else:
            total_query = select(func.count(StudentORM.id))
        
        total_result = await db.execute(total_query)
        total_students = total_result.scalar() or 0
        
        # Get verified count
        verified_query = select(func.count(AttendanceORM.id)).where(
            AttendanceORM.verification_status == 'verified'
        )
        if session_id:
            verified_query = verified_query.where(AttendanceORM.session_id == session_id)
        
        verified_result = await db.execute(verified_query)
        verified_count = verified_result.scalar() or 0
        
        # Get failed count
        failed_query = select(func.count(AttendanceORM.id)).where(
            AttendanceORM.verification_status == 'failed'
        )
        if session_id:
            failed_query = failed_query.where(AttendanceORM.session_id == session_id)
        
        failed_result = await db.execute(failed_query)
        failed_count = failed_result.scalar() or 0
        
        # Calculate percentage
        if total_students > 0:
            percentage = round((verified_count / total_students) * 100, 2)
        else:
            percentage = 0.0
        
        return AttendanceStatistics(
            total_students=total_students,
            verified_count=verified_count,
            failed_count=failed_count,
            attendance_percentage=percentage
        )
    
    async def get_anomalies_grouped_by_student(
        self,
        db: AsyncSession,
        session_id: Optional[int] = None,
        limit: int = 100
    ) -> Dict[int, List[AnomalyORM]]:
        """
        Get anomalies grouped by student, sorted by timestamp within each group.
        """
        query = select(AnomalyORM).where(AnomalyORM.student_id.isnot(None))
        
        if session_id:
            query = query.where(AnomalyORM.session_id == session_id)
        
        query = query.order_by(AnomalyORM.student_id, AnomalyORM.timestamp.desc())
        
        result = await db.execute(query)
        anomalies = result.scalars().all()
        
        grouped: Dict[int, List[AnomalyORM]] = defaultdict(list)
        for anomaly in anomalies:
            if anomaly.student_id:
                grouped[anomaly.student_id].append(anomaly)
        
        return dict(grouped)
    
    async def generate_full_report(
        self,
        db: AsyncSession,
        session_id: Optional[int] = None,
        target_date: Optional[date] = None
    ) -> ReportResponse:
        """
        Generate a complete attendance report.
        """
        # Get attendance records
        if target_date:
            records = await self.get_attendance_by_date(db, target_date)
        else:
            records = await self.get_attendance_records(db, session_id=session_id)
        
        # Get alerts
        proxy_alerts = await self.get_proxy_alerts(db, session_id)
        identity_alerts = await self.get_identity_mismatch_alerts(db, session_id)
        
        # Get statistics
        statistics = await self.get_attendance_statistics(db, session_id)
        
        return ReportResponse(
            attendance_records=records,
            proxy_alerts=proxy_alerts,
            identity_mismatch_alerts=identity_alerts,
            statistics=statistics
        )


# Singleton instance
_report_service: Optional[ReportService] = None


def get_report_service() -> ReportService:
    """Get or create report service instance."""
    global _report_service
    if _report_service is None:
        _report_service = ReportService()
    return _report_service
