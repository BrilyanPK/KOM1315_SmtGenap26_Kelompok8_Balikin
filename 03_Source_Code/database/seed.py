import os
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models import User, RoleEnum, Item, Report, ReportStatusEnum, Inventory
from app.core.security import get_password_hash

def seed_db():
    print("Mereset database (drop all tables)...")
    Base.metadata.drop_all(bind=engine)
    
    print("Membuat ulang skema database (create all)...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Seed Users
        admin_pass = get_password_hash("Admin123!")
        petugas_pass = get_password_hash("Petugas123!")
        pencari_pass = get_password_hash("Pencari123!")

        admin = User(full_name="Administrator", email="admin@ipb.ac.id", hashed_password=admin_pass, role=RoleEnum.ADMIN, mfa_enabled=True)
        petugas = User(full_name="Petugas Keamanan", email="petugas@ipb.ac.id", hashed_password=petugas_pass, role=RoleEnum.PETUGAS, mfa_enabled=False)
        pencari = User(full_name="Budi Mahasiswa", email="budi@ipb.ac.id", hashed_password=pencari_pass, role=RoleEnum.PENCARI, mfa_enabled=False)

        db.add_all([admin, petugas, pencari])
        db.commit()
        print("Berhasil insert Users awal.")

        # Seed Item
        item = Item(name="Dompet Kulit Hitam", category="Aksesoris")
        db.add(item)
        db.commit()

        # Seed Report
        report = Report(
            user_id=pencari.id,
            item_id=item.id,
            location="Kantin GKA",
            description="Dompet panjang warna hitam isi KTP dan KTM",
            status=ReportStatusEnum.HILANG,
            contact_info="081234567890"
        )
        db.add(report)
        db.commit()

        # Seed Found Item & Inventory
        found_item = Item(name="Kunci Motor Honda", category="Kunci")
        db.add(found_item)
        db.commit()

        found_report = Report(
            user_id=petugas.id,
            item_id=found_item.id,
            location="Parkiran CCR",
            description="Ditemukan di dekat pohon beringin",
            finder_id=petugas.id,
            status=ReportStatusEnum.DITEMUKAN,
            contact_info="Pos Satpam Depan"
        )
        db.add(found_report)
        db.commit()

        inv = Inventory(item_id=found_item.id, quantity=1)
        db.add(inv)
        db.commit()
        
        print("Berhasil insert data dummy Reports dan Inventory.")

    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
