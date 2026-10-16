function StatCard({
  title,
  value,
  subtitle
}) {

  return (

    <div className="stat-card">

      <div className="stat-card-top">

        <span className="stat-title">
          {title}
        </span>

        <span className="stat-dot"></span>

      </div>


      <div className="stat-value">
        {value}
      </div>


      <div className="stat-subtitle">
        {subtitle}
      </div>

    </div>

  );

}

export default StatCard;