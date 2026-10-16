import { useState } from "react";

function Prediction() {

  const [form, setForm] = useState({
    age: "",
    gender: "0",
    systolic_bp: "",
    heart_rate: "",
    glucose: "",
    bmi: "",
    oxygen_saturation: "",
    temperature: "",
    previous_conditions: "0",
    smoking: "0",
    hospital_visits: "0"
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  const handleChange = (event) => {

    setForm({
      ...form,
      [event.target.name]: event.target.value
    });

  };


  const handleSubmit = async (event) => {

    event.preventDefault();

    setLoading(true);
    setError("");
    setResult(null);

    try {

      const response = await fetch(
        "http://127.0.0.1:5000/predict",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({

            age: Number(form.age),

            gender: Number(form.gender),

            systolic_bp: Number(form.systolic_bp),

            heart_rate: Number(form.heart_rate),

            glucose: Number(form.glucose),

            bmi: Number(form.bmi),

            oxygen_saturation:
              Number(form.oxygen_saturation),

            temperature:
              Number(form.temperature),

            previous_conditions:
              Number(form.previous_conditions),

            smoking:
              Number(form.smoking),

            hospital_visits:
              Number(form.hospital_visits)

          })
        }
      );


      if (!response.ok) {

        throw new Error(
          "Prediction request failed"
        );

      }


      const data = await response.json();

      setResult(data);

    }

    catch (error) {

      console.error(error);

      setError(
        "Unable to connect to the prediction server. Make sure Python Flask API is running on port 5000."
      );

    }

    finally {

      setLoading(false);

    }

  };


  return (

    <div className="prediction-page">

      <div className="page-header">

        <div>

          <p className="eyebrow">
            ARTIFICIAL INTELLIGENCE
          </p>

          <h1>
            Patient Health Prediction
          </h1>

          <p className="page-description">
            Enter patient health parameters to generate
            an AI-based risk prediction.
          </p>

        </div>

        <div className="model-badge">
          ● Random Forest Model
        </div>

      </div>


      <div className="prediction-layout">

        <form
          className="prediction-form"
          onSubmit={handleSubmit}
        >

          <div className="form-title">

            <div className="form-icon">
              +
            </div>

            <div>
              <h2>Patient Information</h2>
              <p>
                Enter the patient's health measurements
              </p>
            </div>

          </div>


          <div className="form-grid">


            <div className="input-group">

              <label>
                Age
              </label>

              <input
                type="number"
                name="age"
                min="1"
                max="120"
                placeholder="Enter age"
                value={form.age}
                onChange={handleChange}
                required
              />

            </div>


            <div className="input-group">

              <label>
                Gender
              </label>

              <select
                name="gender"
                value={form.gender}
                onChange={handleChange}
              >

                <option value="0">
                  Female
                </option>

                <option value="1">
                  Male
                </option>

              </select>

            </div>


            <div className="input-group">

              <label>
                Systolic Blood Pressure
              </label>

              <input
                type="number"
                name="systolic_bp"
                placeholder="e.g. 120"
                value={form.systolic_bp}
                onChange={handleChange}
                required
              />

            </div>


            <div className="input-group">

              <label>
                Heart Rate
              </label>

              <input
                type="number"
                name="heart_rate"
                placeholder="e.g. 75"
                value={form.heart_rate}
                onChange={handleChange}
                required
              />

            </div>


            <div className="input-group">

              <label>
                Blood Glucose
              </label>

              <input
                type="number"
                name="glucose"
                placeholder="e.g. 100"
                value={form.glucose}
                onChange={handleChange}
                required
              />

            </div>


            <div className="input-group">

              <label>
                BMI
              </label>

              <input
                type="number"
                step="0.1"
                name="bmi"
                placeholder="e.g. 23.5"
                value={form.bmi}
                onChange={handleChange}
                required
              />

            </div>


            <div className="input-group">

              <label>
                Oxygen Saturation
              </label>

              <input
                type="number"
                step="0.1"
                name="oxygen_saturation"
                placeholder="e.g. 98"
                value={form.oxygen_saturation}
                onChange={handleChange}
                required
              />

            </div>


            <div className="input-group">

              <label>
                Temperature
              </label>

              <input
                type="number"
                step="0.1"
                name="temperature"
                placeholder="e.g. 98.6"
                value={form.temperature}
                onChange={handleChange}
                required
              />

            </div>


            <div className="input-group">

              <label>
                Previous Medical Conditions
              </label>

              <input
                type="number"
                min="0"
                name="previous_conditions"
                placeholder="Number of conditions"
                value={form.previous_conditions}
                onChange={handleChange}
              />

            </div>


            <div className="input-group">

              <label>
                Smoking
              </label>

              <select
                name="smoking"
                value={form.smoking}
                onChange={handleChange}
              >

                <option value="0">
                  No
                </option>

                <option value="1">
                  Yes
                </option>

              </select>

            </div>


            <div className="input-group">

              <label>
                Previous Hospital Visits
              </label>

              <input
                type="number"
                min="0"
                name="hospital_visits"
                placeholder="Number of visits"
                value={form.hospital_visits}
                onChange={handleChange}
              />

            </div>

          </div>


          <button
            className="predict-button"
            type="submit"
            disabled={loading}
          >

            {loading
              ? "Analyzing Patient Data..."
              : "Predict Health Risk"
            }

          </button>


          <p className="form-note">
            The prediction is generated by the trained
            Random Forest model through FastAPI.
          </p>

        </form>


        <div className="result-section">

          {!result && !error && (

            <div className="empty-result">

              <div className="result-icon">
                ✦
              </div>

              <h3>
                Prediction Result
              </h3>

              <p>
                Fill in the patient information and click
                "Predict Health Risk" to generate a result.
              </p>

            </div>

          )}


          {error && (

            <div className="prediction-error">

              <h3>
                Connection Error
              </h3>

              <p>
                {error}
              </p>

            </div>

          )}


          {result && (

            <div className="result-card">

              <p className="result-label">
                AI MODEL RESULT
              </p>

              <div className="result-icon success">
                ✓
              </div>

              <h2>
                {result.risk}
              </h2>

              <p className="confidence">
                Model Confidence
              </p>

              <div className="confidence-bar">

                <div
                  style={{
                    width: `${result.confidence}%`
                  }}
                ></div>

              </div>

              <strong className="confidence-value">
                {result.confidence}%
              </strong>

              <div className="result-info">

                <p>
                  Prediction generated successfully
                  using the Random Forest model.
                </p>

              </div>

            </div>

          )}

        </div>

      </div>


      <div className="medical-disclaimer">

        <strong>Important:</strong>

        This system uses synthetic/demo data and is
        intended for educational and software-development
        purposes. It is not a medical diagnosis tool.

      </div>

    </div>

  );
}

export default Prediction;